# Copyright 2025 Kencove, Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestAvataxLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].sudo().set_param(
            "account_avatax_oca.call_counter_limit", "1000"
        )
        cls.log_sale = cls.env["avatax.log"].create(
            {
                "avatax_type": "SalesOrder",
                "avatax_request": "{}",
                "avatax_response": "{}",
            }
        )
        cls.log_invoice = cls.env["avatax.log"].create(
            {
                "avatax_type": "SalesInvoice",
                "avatax_request": "{}",
                "avatax_response": "{}",
            }
        )

    def test_compute_display_name(self):
        self.assertIn(str(self.log_sale.id), self.log_sale.display_name)
        self.assertTrue(self.log_sale.display_name.startswith("Avatax Log"))

    def test_avatax_api_call_counter_below_limit(self):
        # With limit=1000 and only 2 logs, counter should NOT trigger the email branch.
        self.env["ir.config_parameter"].sudo().set_param(
            "account_avatax_oca.call_counter_limit", "1000"
        )
        # Should complete without raising.
        self.env["avatax.log"].avatax_api_call_counter()

    def test_avatax_log_create_selection_types(self):
        log_cancel = self.env["avatax.log"].create({"avatax_type": "cancel"})
        log_others = self.env["avatax.log"].create({"avatax_type": "others"})
        self.assertEqual(log_cancel.avatax_type, "cancel")
        self.assertEqual(log_others.avatax_type, "others")
