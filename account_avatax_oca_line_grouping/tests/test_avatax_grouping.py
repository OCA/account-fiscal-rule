# Copyright 2025
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

from odoo.tests import SavepointCase


class TestAvataxLineGrouping(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        cls.avatax_config = cls.env["avalara.salestax"].create(
            {
                "company_id": cls.company.id,
                "account_number": "123456789",
                "license_key": "dummy-key",
                "service_url": "https://sandbox-rest.avatax.com",
                "company_code": "DEFAULT",
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
                        },
                    ),
                ],
            }
        )
        move.refresh()
        return move

    def test_no_grouping_behaviour(self):
        """Cuando avatax_group_lines es False, cada línea prepara su propio dict."""
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
        """Cuando avatax_group_lines es True, solo la primera línea devuelve el agregado."""
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
