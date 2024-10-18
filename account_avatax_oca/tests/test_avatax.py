# Copyright 2021 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from unittest.mock import patch

from odoo.tests import Form, common

from .mock_avatax import mock_response


class TestAvatax(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fiscal_position = cls.env["account.fiscal.position"].create(
            {
                "name": "Avatax Demo",
                "is_avatax": True,
            }
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Customer",
                "property_account_position_id": cls.fiscal_position.id,
                "property_tax_exempt": True,
                "property_exemption_number": "12321",
                "property_exemption_code_id": cls.env.ref(
                    "account_avatax_oca.resale_type"
                ),
            }
        )

        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.customer.id,
                "invoice_line_ids": [
                    (0, 0, {"name": "Invoice Line", "price_unit": 10, "quantity": 10})
                ],
            }
        )

    def test_100_onchange_customer_exempt(self):
        self.invoice.partner_id = self.customer
        self.assertEqual(
            self.invoice.exemption_code, self.customer.property_exemption_number
        )

    @patch(
        "odoo.addons.account_avatax_oca.models.res_company.Company.get_avatax_config_company"
    )
    @patch(
        "odoo.addons.account_avatax_oca.models.avalara_salestax.AvalaraSalestax.create_transaction"  # noqa: B950
    )
    def test_avatax_compute_tax(
        self, mock_create_transaction, mock_get_avatax_config_company
    ):
        avatax_config = self.env["avalara.salestax"].create(
            {
                "account_number": "123456",
                "license_key": "123456",
                "company_code": "DEFAULT",
                "disable_tax_calculation": False,
                "invoice_calculate_tax": False,
            }
        )
        mock_get_avatax_config_company.return_value = avatax_config

        # Force empty taxes to check only avatax taxes
        self.invoice.invoice_line_ids.write(
            {
                "tax_ids": [(6, 0, [])],
            }
        )

        invoice_line_data = [
            {
                "product_id": self.env["product.product"].create({"name": "Product 1"}),
                "quantity": 5,
                "price_unit": 102.5,
                "rate": 0.06448,
            },
            {
                "product_id": self.env["product.product"].create({"name": "Product 2"}),
                "quantity": 4,
                "price_unit": 25.5,
                "rate": 0.03448,
            },
        ]

        self.invoice.invoice_line_ids.unlink()
        invoice_form = Form(self.invoice)

        for line_data in invoice_line_data:
            with invoice_form.invoice_line_ids.new() as line:
                line.product_id = line_data.get("product_id")
                line.quantity = line_data.get("quantity")
                line.price_unit = line_data.get("price_unit")
                line.tax_ids.clear()
        self.assertFalse(invoice_form.calculate_tax_on_save)
        self.invoice = invoice_form.save()
        self.assertFalse(self.invoice.calculate_tax_on_save)
        mock_create_transaction.return_value = mock_response(
            [
                {
                    "product": line.product_id,
                    "quantity": line.quantity,
                    "price_unit": line.price_unit,
                    "discount_amount": line.price_subtotal
                    - ((line.price_unit * line.quantity) * (1 - line.discount * 100.0)),
                    "rate_expected": line_data.get("rate"),
                    "line_id": line.id,
                }
                for line, line_data in zip(
                    self.invoice.invoice_line_ids, invoice_line_data
                )
            ]
        )

        self.invoice.invalidate_model(["invoice_line_ids"])
        for line in self.invoice.invoice_line_ids:
            self.assertFalse(bool(line.tax_ids))
        self.invoice.action_post()

        for line in self.invoice.invoice_line_ids:
            self.assertTrue(bool(line.tax_ids))

        self.assertEqual(
            self.invoice.amount_tax + self.invoice.amount_untaxed,
            self.invoice.amount_residual,
        )
        mock_get_avatax_config_company.assert_called()
        mock_create_transaction.assert_called()

        self.invoice.button_draft()

        avatax_config.write(
            {
                "invoice_calculate_tax": True,
            }
        )

        self.invoice.invoice_line_ids.unlink()

        invoice_form = Form(self.invoice)
        for line_data in invoice_line_data:
            with invoice_form.invoice_line_ids.new() as line:
                line.product_id = line_data.get("product_id")
                line.quantity = line_data.get("quantity")
                line.price_unit = line_data.get("price_unit")
                line.tax_ids.clear()
        self.assertTrue(invoice_form.calculate_tax_on_save)
        self.invoice = invoice_form.save()
        mock_create_transaction.return_value = mock_response(
            [
                {
                    "product": line.product_id,
                    "quantity": line.quantity,
                    "price_unit": line.price_unit,
                    "discount_amount": line.price_subtotal
                    - ((line.price_unit * line.quantity) * (1 - line.discount * 100.0)),
                    "rate_expected": line_data.get("rate"),
                    "line_id": line.id,
                }
                for line, line_data in zip(
                    self.invoice.invoice_line_ids, invoice_line_data
                )
            ]
        )
        self.assertFalse(self.invoice.calculate_tax_on_save)
        self.invoice.action_post()
        for line in self.invoice.invoice_line_ids:
            self.assertTrue(bool(line.tax_ids))

        self.assertEqual(
            self.invoice.amount_tax + self.invoice.amount_untaxed,
            self.invoice.amount_residual,
        )
