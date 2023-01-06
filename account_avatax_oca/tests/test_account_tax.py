# Copyright 2021 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import exceptions
from odoo.tests import common


class TestAvatax(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tax = cls.env["account.tax"]
        cls.company1 = cls.env.ref("base.main_company")
        cls.company2 = cls.env["res.company"].create({"name": "Company Avatax 2"})

    def test_get_avatax_tax_rate(self):
        tax75 = self.Tax.get_avalara_tax(7.5, "out_invoice")
        self.assertEqual(tax75.amount, 7.5)

    def test_get_avatax_template(self):
        tax = self.Tax.get_avalara_tax(0, "out_invoice")
        self.assertEqual(tax.name, "AVATAX")

    def test_get_avatax_template_missing(self):
        with self.assertRaises(exceptions.UserError):
            self.Tax.with_company(self.company2).get_avalara_tax(0, "out_invoice")
