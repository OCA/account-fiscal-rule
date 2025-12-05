from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestTaxAmount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create Taxes
        cls.tax_vat_20 = cls.env["account.tax"].create(
            {
                "name": "VAT 20%",
                "amount_type": "percent",
                "amount": 20.0,
                "type_tax_use": "sale",
            }
        )
        cls.ecotax = cls.env["account.tax"].create(
            {
                "name": "Ecotax",
                "amount_type": "fixed",
                "use_product_amount": True,
                "type_tax_use": "sale",
                "amount": 3.0,
            }
        )
        cls.ecotax_purchase = cls.env["account.tax"].create(
            {
                "name": "Ecotax Purchase",
                "amount_type": "fixed",
                "use_product_amount": True,
                "type_tax_use": "purchase",
                "amount": 7.0,
            }
        )

        # Create Product Template
        cls.product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Bed",
                "taxes_id": [Command.set(cls.tax_vat_20.ids + cls.ecotax.ids)],
            }
        )

        # Get Variant
        cls.variant_a = cls.product_tmpl.product_variant_id
        cls.variant_a.tax_amount_ids.filtered(
            lambda tax_amount: tax_amount.tax_id == cls.ecotax
        ).amount = 5.0

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

    def test_invoice_ecotax(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.variant_a.id,
                            "quantity": 3,
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )

        line_a = invoice.invoice_line_ids.filtered(
            lambda invoice_line: invoice_line.product_id == self.variant_a
        )
        self.assertIn(self.tax_vat_20, line_a.tax_ids)
        self.assertIn(self.ecotax, line_a.tax_ids)
        self.assertEqual(line_a.price_subtotal, 300.0)
        self.assertEqual(invoice.amount_total, 375.0)

    def test_add_ecotax_purchase_generate_account_tax_product_amount(self):
        self.variant_a.supplier_taxes_id |= self.ecotax_purchase
        # self.variant_a.flush()
        # self.variant_a._maintain_product_variant_tax_amount_consistency()
        self.assertIn(self.ecotax_purchase, self.variant_a.tax_amount_ids.tax_id)
        self.assertEqual(
            self.variant_a.tax_amount_ids.filtered(
                lambda tax_amount: tax_amount.tax_id == self.ecotax_purchase
            ).amount,
            7.0,
        )
