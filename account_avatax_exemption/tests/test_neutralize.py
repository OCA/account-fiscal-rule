# Copyright 2026 FactorLibre
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.modules.neutralize import get_neutralization_queries
from odoo.tests import common


class TestNeutralize(common.TransactionCase):
    def test_01_neutralize_disables_the_exemption_exports(self):
        config = self.env["avalara.salestax"].create(
            {
                "account_number": "3300000000",
                "license_key": "5Q4R3S2T1U0V9W8X",
                "company_code": "NEUTRALIZE-EXEMPTION",
                "tax_item_export": True,
                "exemption_export": True,
                "exemption_rule_export": True,
            }
        )
        queries = list(get_neutralization_queries(["account_avatax_exemption"]))
        self.assertEqual(len(queries), 1)
        self.env.flush_all()
        self.env.cr.execute(queries[0])
        self.env.invalidate_all()
        self.assertFalse(config.tax_item_export)
        self.assertFalse(config.exemption_export)
        self.assertFalse(config.exemption_rule_export)
