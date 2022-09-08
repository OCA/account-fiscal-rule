# Copyright 2022 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common

from ..models.avatax_rest_api import AvaTaxRESTService


class TestAvatax(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.API = AvaTaxRESTService()

    def test_enrich_result_lines_with_tax_rate(self):
        avatax_result = {
            "lines": [
                {
                    "details": [
                        {
                            "rate": 0.056,
                            "tax": 0.0,
                            "taxCalculated": 0.0,
                            "taxName": "AZ STATE TAX",
                            "taxableAmount": 0.0,
                        },
                        {
                            "rate": 0.007,
                            "tax": 0.0,
                            "taxCalculated": 0.0,
                            "taxName": "AZ COUNTY TAX",
                            "taxableAmount": 0.0,
                        },
                        {
                            "rate": 0.018,
                            "tax": 0.16,
                            "taxCalculated": 0.16,
                            "taxName": "AZ CITY TAX",
                            "taxableAmount": 9.0,
                        },
                    ],
                    "isItemTaxable": True,
                    "lineAmount": 9.0,
                    "tax": 0.16,
                    "taxCalculated": 0.16,
                    "taxableAmount": 9.0,
                }
            ]
        }
        result = self.API._enrich_result_lines_with_tax_rate(avatax_result)
        rate = result["lines"][0]["rate"]
        self.assertEqual(rate, 1.8)
