# Copyright 2022 Coop IT Easy SC (http://coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestAccountDefaultFiscalPosition(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # MODELS
        cls.res_partner_model = cls.env["res.partner"]
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        cls.fiscal_position_line_model = cls.env["fiscal.position.line"]
        # INSTANCES
        # Company
        cls.company_main = cls.env.ref("base.main_company")
        # Country
        cls.country_be = cls.env.ref("base.be")
        cls.country_fr = cls.env.ref("base.fr")
        # Fiscal Positions
        cls.fiscal_position_test = cls.fiscal_position_model.create(
            {
                "name": "Test",
                "auto_apply": False,
                "sequence": 1,
            }
        )
        cls.fiscal_position_line_be = cls.fiscal_position_line_model.create(
            {
                "fiscal_position_id": cls.fiscal_position_test.id,
                "country_id": cls.country_be.id,
            }
        )
        cls.fiscal_position_line_fr = cls.fiscal_position_line_model.create(
            {
                "fiscal_position_id": cls.fiscal_position_test.id,
                "country_id": cls.country_fr.id,
            }
        )

    def test_partner_be(self):
        partner_id = self.res_partner_model.create(
            {
                "name": "Dominique Dupond",
                "is_company": False,
                "vat": "BE0477472701",
                "country_id": self.country_be.id,
            }
        )
        self.assertEqual(
            partner_id.property_account_position_id, self.fiscal_position_test
        )

    def test_partner_fr(self):
        partner_id = self.res_partner_model.create(
            {
                "name": "Dominique Dupond",
                "is_company": False,
                "vat": "FR23334175221",
                "country_id": self.country_fr.id,
            }
        )
        self.assertEqual(
            partner_id.property_account_position_id, self.fiscal_position_test
        )

    def test_partner_no_country(self):
        partner_id = self.res_partner_model.create(
            {
                "name": "Dominique Dupond",
                "is_company": False,
                "vat": "FR23334175221",
                "country_id": False,
            }
        )
        self.assertEqual(
            partner_id.property_account_position_id,
            self.fiscal_position_model,
        )
