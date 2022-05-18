# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase

from ...account_avatax.models.avatax_rest_api import AvaTaxRESTService


class TestAvatax(SavepointCase):
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
                            "rate": 0.06,
                            "tax": 15.0,
                            "taxCalculated": 15.0,
                            "taxName": "FL STATE TAX",
                            "taxableAmount": 250.0,
                        },
                        {
                            "rate": 0.005,
                            "tax": 1.25,
                            "taxCalculated": 1.25,
                            "taxName": "FL COUNTY TAX",
                            "taxableAmount": 250.0,
                        },
                    ],
                    "isItemTaxable": True,
                    "lineAmount": 250.0,
                    "tax": 16.25,
                    "taxCalculated": 16.25,
                    "taxableAmount": 250.0,
                }
            ]
        }
        result = self.API._enrich_result_lines_with_tax_rate(avatax_result)
        rate = result["lines"][0]["rate"]
        self.assertEqual(rate, 6.5)
