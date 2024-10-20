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

    def test_get_avatax_config_company_missing(self):
        logger_name = "odoo.addons.account_avatax_oca.models.res_company"
        with self.assertLogs(logger_name) as watcher:
            res = self.company2.get_avatax_config_company()
            expected_msg = "Company Company Avatax 2 has no Avatax configuration."
            self.assertIn(expected_msg, watcher.output[0])
            self.assertFalse(res.invoice_calculate_tax)
            self.assertFalse(res.validation_on_save)

    def test_get_avatax_config_company_no_config(self):
        logger_name = "odoo.addons.account_avatax_oca.models.res_company"
        self.company2.allow_avatax_configuration = False
        res = self.company2.get_avatax_config_company()
        self.assertFalse(res.invoice_calculate_tax)
        self.assertFalse(res.validation_on_save)
        # test no log
        with self.assertRaises(AssertionError):
            with self.assertLogs(logger_name, "DEBUG") as watcher:
                self.company2.get_avatax_config_company()
                expected_msg = "Company Company Avatax 2 has no Avatax configuration."
                self.assertNotIn(
                    expected_msg,
                    watcher.output[0] if watcher.output else watcher.output,
                )
