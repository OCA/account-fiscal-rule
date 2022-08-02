# Copyright 2021 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestAvatax(common.TransactionCase):
    def test_customer_existing_code(self):
        "Create Customer with an already existing code (data import)"
        val_customer = {"name": "New Customer", "customer_code": "ABC"}
        new_customer = self.env["res.partner"].create(val_customer)
        self.assertEqual(new_customer.customer_code, "ABC")
