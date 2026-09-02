# Copyright 2026 FactorLibre
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.modules.neutralize import get_neutralization_queries
from odoo.tests import common


class TestNeutralize(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env["avalara.salestax"].create(
            {
                "account_number": "1100000000",
                "license_key": "1A2B3C4D5E6F7G8H",
                "company_code": "NEUTRALIZE-A",
                "disable_tax_calculation": False,
                "disable_tax_reporting": False,
            }
        )

    def _run_neutralization(self):
        queries = list(get_neutralization_queries(["account_avatax_oca"]))
        self.assertEqual(len(queries), 1)
        self.env.flush_all()
        self.env.cr.execute(queries[0])
        self.env.invalidate_all()

    def test_01_neutralize_disables_calculation_and_reporting(self):
        self._run_neutralization()
        self.assertTrue(self.config.disable_tax_calculation)
        self.assertTrue(self.config.disable_tax_reporting)
        self.assertFalse(self.config.license_key)
        self.assertNotEqual(self.config.account_number, "1100000000")

    def test_02_neutralize_keeps_account_number_unique_per_company(self):
        # A company may hold several configurations (account_number_company_uniq).
        second = self.env["avalara.salestax"].create(
            {
                "account_number": "2200000000",
                "license_key": "9I8J7K6L5M4N3O2P",
                "company_code": "NEUTRALIZE-B",
                "company_id": self.config.company_id.id,
            }
        )
        self._run_neutralization()
        self.assertNotEqual(self.config.account_number, second.account_number)
        self.assertNotEqual(second.account_number, "2200000000")
        self.assertFalse(second.license_key)
