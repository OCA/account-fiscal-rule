# Copyright 2026 FactorLibre
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command
from odoo.tests import common


class TestSaleOrderBaseAmount(common.TransactionCase):
    """Taxable base reported to AvaTax from the sale order path.

    The invoice copies price and taxes from the order line without recomputing
    them, so both paths have to agree: otherwise the order to invoice channel
    keeps reporting a gross amount even after the invoice path is fixed.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Avatax Base Customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Avatax Base Product", "list_price": 340.0}
        )
        tax_vals = {
            "amount_type": "percent",
            "type_tax_use": "sale",
            "company_id": cls.env.company.id,
        }
        cls.tax_included = cls.env["account.tax"].create(
            dict(tax_vals, name="Test 8.75% included", amount=8.75, price_include=True)
        )
        cls.tax_excluded = cls.env["account.tax"].create(
            dict(tax_vals, name="Test 8.75% excluded", amount=8.75, price_include=False)
        )

    def _create_order(self, taxes, price_unit=340.0, quantity=1.0, discount=0.0):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": quantity,
                            "price_unit": price_unit,
                            "discount": discount,
                            "tax_id": [Command.set(taxes.ids)],
                        }
                    )
                ],
            }
        )

    def test_01_sale_amount_price_include(self):
        """Gross 340 with an 8.75% included tax reports a net base of 312.64."""
        order = self._create_order(self.tax_included)
        line = order.order_line
        self.assertAlmostEqual(line._avatax_prepare_line()["amount"], 312.64, places=2)
        self.assertAlmostEqual(
            line._avatax_prepare_line()["amount"], line.price_subtotal, places=2
        )
        prepared = line._avatax_prepare_line()
        self.assertAlmostEqual(prepared["amount"], 312.64, places=2)

    def test_02_sale_amount_price_exclude(self):
        """Without a price included tax the reported base does not change."""
        order = self._create_order(self.tax_excluded, quantity=3.0)
        line = order.order_line
        legacy_amount = (
            line.price_unit * line.product_uom_qty * (1 - line.discount / 100.0)
        )
        self.assertAlmostEqual(
            line._avatax_prepare_line()["amount"], legacy_amount, places=2
        )

    def test_03_sale_amount_discount(self):
        """The net base is computed on the already discounted price."""
        order = self._create_order(self.tax_included, discount=10.0)
        line = order.order_line
        # 340 * 0.9 = 306 gross -> 306 / 1.0875 = 281.38 net
        self.assertAlmostEqual(line._avatax_prepare_line()["amount"], 281.38, places=2)

    def test_04_sale_amount_quantity(self):
        """The reported amount is a line total, rounded once for the line.

        The AvaTax ``amount`` field is the total for the line and ``quantity``
        travels as a separate field, so the quantity must be inside the amount
        and must not be applied twice.
        """
        order = self._create_order(self.tax_included, quantity=2.0)
        line = order.order_line
        # 680 gross -> 625.29 net, not 2 * 312.64 = 625.28
        self.assertAlmostEqual(line._avatax_prepare_line()["amount"], 625.29, places=2)
        prepared = line._avatax_prepare_line()
        self.assertAlmostEqual(prepared["amount"], 625.29, places=2)
        self.assertEqual(prepared["qty"], 2.0)

    def test_05_sale_amount_matches_invoice(self):
        """The order line and its invoice line report the same amount.

        This is the order to invoice channel: the invoice inherits price and
        taxes from the order, so a mismatch here means the same sale is reported
        twice with two different taxable bases.
        """
        order = self._create_order(self.tax_included, quantity=2.0)
        order.action_confirm()
        invoice = order._create_invoices()
        order_amount = order.order_line._avatax_prepare_line()["amount"]
        invoice_amount = invoice.invoice_line_ids._avatax_prepare_line(sign=1)["amount"]
        self.assertAlmostEqual(order_amount, invoice_amount, places=2)
        self.assertAlmostEqual(order_amount, 625.29, places=2)

    def test_06_override_line_taxes_documented(self):
        """Known limitation: an exclusive AvaTax tax breaks the document itself.

        With ``override_line_taxes`` enabled AvaTax replaces the line tax with
        one of its own, copied from the 0% AvaTax template. If that template is
        not flagged as price included, Odoo loses the signal that ``price_unit``
        is gross: its own ``price_subtotal`` starts treating the gross amount as
        a net base and the order total changes.

        This is a pre-existing defect, independent of the taxable base reported
        to AvaTax, and no base computation can fix it without touching
        ``price_unit``. The test pins the behaviour so it stays a known
        limitation instead of a surprise.
        """
        order = self._create_order(self.tax_included)
        line = order.order_line
        self.assertAlmostEqual(line.price_subtotal, 312.64, places=2)
        self.assertAlmostEqual(order.amount_total, 340.0, places=2)

        avatax_exclusive = self.env["account.tax"].create(
            {
                "name": "AvaTax 8.75% exclusive",
                "amount_type": "percent",
                "amount": 8.75,
                "price_include": False,
                "type_tax_use": "sale",
                "company_id": self.env.company.id,
                "is_avatax": True,
            }
        )
        line.tax_id = [Command.set(avatax_exclusive.ids)]

        # The document itself now reads the gross amount as a net base.
        self.assertAlmostEqual(line.price_subtotal, 340.0, places=2)
        self.assertGreater(order.amount_total, 340.0)
        # And the reported base mirrors the document, as it must.
        self.assertAlmostEqual(line._avatax_prepare_line()["amount"], 340.0, places=2)
