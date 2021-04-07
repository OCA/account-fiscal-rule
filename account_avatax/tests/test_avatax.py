# Copyright 2021 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo.tests.common import SavepointCase


class TestAvatax(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Customer",
                "property_tax_exempt": True,
                "property_exemption_number": "12321",
                "property_exemption_code_id": cls.env.ref("account_avatax.resale_type"),
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
