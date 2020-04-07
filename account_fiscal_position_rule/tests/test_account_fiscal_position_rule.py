# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountFiscalPositionRule(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountFiscalPositionRule, cls).setUpClass()

        # MODELS
        cls.account_move_model = cls.env["account.move"]
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        cls.fiscal_position_rule_model = cls.env["account.fiscal.position.rule"]
        cls.fiscal_position_rule_template_model = cls.env[
            "account.fiscal.position.rule.template"
        ]
        cls.fiscal_position_template_model = cls.env["account.fiscal.position.template"]
        cls.wizard_model = cls.env["wizard.account.fiscal.position.rule"]

        # INSTANCES
        # Company
        cls.company_main = cls.env.ref("base.main_company")
        # Countries
        cls.country_fr = cls.env.ref("base.fr")
        cls.country_tw = cls.env.ref("base.tw")
        cls.country_us = cls.env.ref("base.us")
        # Partners
        cls.partner_01 = cls.env.ref("base.res_partner_1")
        cls.partner_01.country_id = cls.country_us
        cls.partner_02 = cls.env.ref("base.res_partner_2")
        cls.partner_03 = cls.env.ref("base.res_partner_address_34")
        # Chart template
        cls.chart_template_01 = cls.env.ref(
            "l10n_generic_coa.configurable_chart_template"
        )
        # Fiscal position templates
        cls.fp_template_01 = cls.fiscal_position_template_model.create(
            {"name": "Normal Taxes", "chart_template_id": cls.chart_template_01.id}
        )
        cls.fp_template_02 = cls.fiscal_position_template_model.create(
            {"name": "Tax Exempt", "chart_template_id": cls.chart_template_01.id}
        )
        # Fiscal rules
        cls.fiscal_position_01 = cls.fiscal_position_model.create(
            {"name": "Tax Exempt"}
        )
        cls.fiscal_position_02 = cls.fiscal_position_model.create(
            {"name": "Normal Taxes"}
        )
        # Rule templates
        cls.fp_rule_template_01 = cls.fiscal_position_rule_template_model.create(
            {
                "name": "Rule 01",
                "use_sale": True,
                "from_country": cls.country_us.id,
                "to_invoice_country": cls.country_tw.id,
                "fiscal_position_id": cls.fp_template_02.id,
            }
        )
        cls.fp_rule_template_01 = cls.fiscal_position_rule_template_model.create(
            {
                "name": "Rule 02",
                "use_sale": True,
                "from_country": cls.country_us.id,
                "to_invoice_country": cls.country_fr.id,
                "fiscal_position_id": cls.fp_template_01.id,
            }
        )
        # Fiscal position rule
        cls.fp_rule_01 = cls.fiscal_position_rule_model.create(
            {
                "name": "Fake rule",
                "company_id": cls.company_main.id,
                "fiscal_position_id": cls.fiscal_position_01.id,
                "use_sale": True,
            }
        )

    def test_01(self):
        """
        Data:
            - Existing rule templates
        Test case:
            - Generate rules based on templates
        Expected result:
            - Rules correctly generated
        """
        fp_rule_wizard = self.wizard_model.create({"company_id": self.company_main.id})
        fp_rule_wizard.action_create()
        # check rules
        rule = self.fiscal_position_rule_model.search(
            [("name", "=", "Rule 01"), ("from_country", "=", self.country_us.id)]
        )
        self.assertEqual(len(rule), 1)
        self.assertEqual(rule.fiscal_position_id, self.fiscal_position_01)
        rule = self.fiscal_position_rule_model.search(
            [("name", "=", "Rule 02"), ("from_country", "=", self.country_us.id)]
        )
        self.assertEqual(len(rule), 1)
        self.assertEqual(rule.fiscal_position_id, self.fiscal_position_02)

    def test_02(self):
        """
        Data:
            - /
        Test case:
            - Trigger the mapping of invoice address
        Expected result:
            - The right rule is returned
        """
        kw = {
            "company_id": self.company_main,
            "partner_id": self.partner_01,
            "partner_invoice_id": self.partner_01,
        }
        res = self.fp_rule_01.fiscal_position_map(**kw)
        self.assertEqual(res, self.fiscal_position_01)

    def test_03(self):
        """
        Data:
            - /
        Test case:
            - Trigger the mapping of shipping address
        Expected result:
            - The right rule is returned
        """
        kw = {
            "company_id": self.company_main,
            "partner_id": self.partner_03,
            "partner_shipping_id": self.partner_03,
        }
        res = self.fp_rule_01.fiscal_position_map(**kw)
        self.assertEqual(res, self.fiscal_position_01)

    def test_04(self):
        """
        Data:
            - /
        Test case:
            - Trigger the mapping of specific partner
        Expected result:
            - The right rule is returned
        """
        self.partner_02.property_account_position_id = self.fiscal_position_01
        kw = {"company_id": self.company_main, "partner_id": self.partner_02}
        res = self.fp_rule_01.fiscal_position_map(**kw)
        self.assertEqual(res, self.fiscal_position_01)
