# Copyright 2025
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

from unittest.mock import patch

from odoo.tests import common
from odoo.tools import float_round


class TestAvataxLineGrouping(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        cls.avatax_config = cls.env["avalara.salestax"].create(
            {
                "company_id": cls.company.id,
                "account_number": "123456789",
                "license_key": "dummy-key",
                "company_code": "DEFAULT",
                "disable_tax_calculation": False,
                "invoice_calculate_tax": False,
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )

        cls.fiscal_position = cls.env["account.fiscal.position"].create(
            {
                "name": "Avatax FP",
                "is_avatax": True,
            }
        )
        cls.partner.property_account_position_id = cls.fiscal_position

        cls.product_1 = cls.env["product.product"].create(
            {"name": "Prod 1", "list_price": 100.0}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Prod 2", "list_price": 50.0}
        )

        cls.income_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "income"),
                ("company_id", "=", cls.company.id),
                ("deprecated", "=", False),
            ],
            limit=1,
        )
        if not cls.income_account:
            cls.income_account = cls.env["account.account"].create(
                {
                    "name": "Avatax Income",
                    "code": "AVA999",
                    "account_type": "income",
                    "company_id": cls.company.id,
                }
            )

        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Avatax Test Pricelist",
                "currency_id": cls.company.currency_id.id,
            }
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _create_invoice_two_lines(self):
        """Crear una factura de prueba con 2 líneas de producto."""
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Line 1",
                            "product_id": self.product_1.id,
                            "price_unit": 100.0,
                            "quantity": 2.0,
                            "account_id": self.income_account.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Line 2",
                            "product_id": self.product_2.id,
                            "price_unit": 50.0,
                            "quantity": 3.0,
                            "account_id": self.income_account.id,
                        },
                    ),
                ],
            }
        )
        move.refresh()
        return move

    def _create_sale_order_two_lines(self):
        """Crear una SO de prueba con 2 líneas de producto."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "SO Line 1",
                            "product_id": self.product_1.id,
                            "product_uom_qty": 2.0,
                            "price_unit": 100.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "SO Line 2",
                            "product_id": self.product_2.id,
                            "product_uom_qty": 3.0,
                            "price_unit": 50.0,
                        },
                    ),
                ],
            }
        )
        order.refresh()
        return order

    def test_no_grouping_behaviour(self):
        """Con avatax_group_lines = False, cada línea prepara su propio dict."""
        self.company.avatax_group_lines = False
        self.avatax_config.avatax_group_lines = False

        invoice = self._create_invoice_two_lines()
        line1, line2 = invoice.invoice_line_ids

        res1 = line1._avatax_prepare_line(sign=1, doc_type="SalesInvoice")
        res2 = line2._avatax_prepare_line(sign=1, doc_type="SalesInvoice")

        self.assertTrue(
            res1,
            "First line should return a dict when grouping is disabled",
        )
        self.assertTrue(
            res2,
            "Second line should return a dict when grouping is disabled",
        )
        self.assertNotEqual(
            res1,
            res2,
            "Each line should have its own payload when grouping is disabled",
        )

    def test_grouping_behaviour(self):
        """Con avatax_group_lines = True solo la primera línea devuelve el agregado."""
        self.company.avatax_group_lines = True
        self.avatax_config.avatax_group_lines = True

        invoice = self._create_invoice_two_lines()
        line1, line2 = invoice.invoice_line_ids

        total_expected = line1._get_avatax_amount() + line2._get_avatax_amount()

        res1 = line1._avatax_prepare_line(sign=1, doc_type="SalesInvoice")
        res2 = line2._avatax_prepare_line(sign=1, doc_type="SalesInvoice")

        self.assertTrue(res1, "First line should return an aggregated dict")
        self.assertEqual(
            res1.get("qty"),
            1.0,
            "Aggregated line should use qty = 1",
        )
        self.assertAlmostEqual(
            res1.get("amount", 0.0),
            total_expected,
            places=2,
            msg="Aggregated amount should be the sum of all lines' Avatax base",
        )

        self.assertEqual(
            res2,
            {},
            "Non-first lines must return empty dict when grouping is enabled",
        )

    def test_grouping_with_negative_quantity(self):
        """La lógica de agrupación debe considerar cantidades negativas."""
        self.company.avatax_group_lines = True
        self.avatax_config.avatax_group_lines = True

        invoice = self._create_invoice_two_lines()
        line1, line2 = invoice.invoice_line_ids
        line2.quantity = -3.0

        res1 = line1._avatax_prepare_line(sign=1, doc_type="SalesInvoice")
        res2 = line2._avatax_prepare_line(sign=1, doc_type="SalesInvoice")

        expected_amount = line1._get_avatax_amount() + line2._get_avatax_amount()

        self.assertTrue(res1)
        self.assertAlmostEqual(res1["amount"], expected_amount, places=2)
        self.assertEqual(res2, {})

    def test_invoice_compute_tax_grouping(self):
        """_avatax_compute_tax reparte el impuesto de una sola línea de Avatax."""
        self.company.avatax_group_lines = True
        self.avatax_config.avatax_group_lines = True

        invoice = self._create_invoice_two_lines()
        line1, line2 = invoice.invoice_line_ids

        base1 = line1._get_avatax_amount()
        base2 = line2._get_avatax_amount()
        total_base = base1 + base2
        total_tax = 10.0

        def fake_create_transaction(config, *args, **kwargs):
            return {
                "totalTax": total_tax,
                "lines": [
                    {
                        "lineNumber": "1",
                        "taxCalculated": total_tax,
                        "taxableAmount": total_base,
                        "tax": total_tax,
                    }
                ],
            }

        def fake_update_tax_details(move_self, tax, line, tax_result_line):
            return tax, line

        with patch.object(
            type(self.avatax_config), "create_transaction", fake_create_transaction
        ), patch.object(type(invoice), "update_tax_details", fake_update_tax_details):
            res = invoice._avatax_compute_tax(commit=False)

        self.assertEqual(res["totalTax"], total_tax)

        self.assertAlmostEqual(
            line1.avatax_amt_line + line2.avatax_amt_line,
            total_tax,
            places=2,
        )

        rounding = invoice.currency_id.rounding
        expected_line1 = float_round(
            total_tax * (base1 / total_base),
            precision_rounding=rounding,
        )
        expected_line2 = total_tax - expected_line1

        self.assertAlmostEqual(line1.avatax_amt_line, expected_line1, places=2)
        self.assertAlmostEqual(line2.avatax_amt_line, expected_line2, places=2)

    def test_invoice_compute_tax_no_grouping(self):
        """Cuando no hay agrupación, cada línea usa su propio resultado de Avatax."""
        self.company.avatax_group_lines = False
        self.avatax_config.avatax_group_lines = False

        invoice = self._create_invoice_two_lines()
        line1, line2 = invoice.invoice_line_ids

        def fake_create_transaction(config, *args, **kwargs):
            return {
                "totalTax": 15.0,
                "lines": [
                    {
                        "lineNumber": str(line1.id),
                        "taxCalculated": 10.0,
                        "taxableAmount": line1._get_avatax_amount(),
                        "tax": 10.0,
                    },
                    {
                        "lineNumber": str(line2.id),
                        "taxCalculated": 5.0,
                        "taxableAmount": line2._get_avatax_amount(),
                        "tax": 5.0,
                    },
                ],
            }

        def fake_update_tax_details(move_self, tax, line, tax_result_line):
            return tax, line

        with patch.object(
            type(self.avatax_config), "create_transaction", fake_create_transaction
        ), patch.object(type(invoice), "update_tax_details", fake_update_tax_details):
            res = invoice._avatax_compute_tax(commit=False)

        self.assertEqual(res["totalTax"], 15.0)
        self.assertAlmostEqual(line1.avatax_amt_line, 10.0, places=2)
        self.assertAlmostEqual(line2.avatax_amt_line, 5.0, places=2)
        self.assertAlmostEqual(invoice.avatax_amount, 15.0, places=2)

    def test_sale_order_compute_tax_grouping(self):
        """En SO, el impuesto se reparte entre las líneas cuando Avatax devuelve 1 línea."""
        self.company.avatax_group_lines = True
        self.avatax_config.avatax_group_lines = True

        order = self._create_sale_order_two_lines()
        line1, line2 = order.order_line

        def _line_base(line):
            return (
                line.price_unit
                * line.product_uom_qty
                * (1 - (line.discount or 0.0) / 100.0)
            )

        base1 = _line_base(line1)
        base2 = _line_base(line2)
        total_base = base1 + base2
        total_tax = 7.0

        def fake_create_transaction(config, *args, **kwargs):
            return {
                "totalTax": total_tax,
                "lines": [
                    {
                        "lineNumber": "1",
                        "taxCalculated": total_tax,
                        "taxableAmount": total_base,
                        "tax": total_tax,
                    }
                ],
            }

        def fake_update_tax_details(order_self, tax, line, tax_result_line):
            return tax, line

        with patch.object(
            type(self.avatax_config), "create_transaction", fake_create_transaction
        ), patch.object(type(order), "update_tax_details", fake_update_tax_details):
            res = order._avatax_compute_tax()

        self.assertTrue(res)
        self.assertAlmostEqual(order.tax_amount, total_tax, places=2)
        self.assertAlmostEqual(
            line1.tax_amt + line2.tax_amt,
            total_tax,
            places=2,
        )
