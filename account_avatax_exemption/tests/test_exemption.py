from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestExemptionRule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.exemption_code = cls.env["exemption.code"].create(
            {"name": "Test Code", "code": "TEST"}
        )

    def test_create_assigns_sequence(self):
        rule = self.env["exemption.code.rule"].create(
            {"exemption_code_id": self.exemption_code.id}
        )
        self.assertTrue(rule.name)
        self.assertNotEqual(rule.name, self.env._("New"))

    def test_rate_constraint_valid(self):
        rule = self.env["exemption.code.rule"].create(
            {"exemption_code_id": self.exemption_code.id, "avatax_rate": 50.0}
        )
        self.assertEqual(rule.avatax_rate, 50.0)

    def test_rate_constraint_negative(self):
        with self.assertRaises(ValidationError):
            self.env["exemption.code.rule"].create(
                {"exemption_code_id": self.exemption_code.id, "avatax_rate": -1.0}
            )

    def test_rate_constraint_over_100(self):
        with self.assertRaises(ValidationError):
            self.env["exemption.code.rule"].create(
                {"exemption_code_id": self.exemption_code.id, "avatax_rate": 101.0}
            )

    def test_reset_to_draft(self):
        rule = self.env["exemption.code.rule"].create(
            {"exemption_code_id": self.exemption_code.id, "state": "cancel"}
        )
        rule.reset_to_draft()
        self.assertEqual(rule.state, "draft")

    def test_export_rule_wrong_state(self):
        rule = self.env["exemption.code.rule"].create(
            {"exemption_code_id": self.exemption_code.id, "state": "done"}
        )
        with self.assertRaises(UserError):
            rule.export_exemption_rule()

    def test_export_rule_no_config(self):
        rule = self.env["exemption.code.rule"].create(
            {"exemption_code_id": self.exemption_code.id}
        )
        with self.assertRaises(UserError):
            rule.export_exemption_rule()

    def test_cancel_rule_wrong_state(self):
        rule = self.env["exemption.code.rule"].create(
            {"exemption_code_id": self.exemption_code.id, "state": "draft"}
        )
        with self.assertRaises(UserError):
            rule.cancel_exemption_rule()

    def test_cancel_rule_no_config(self):
        rule = self.env["exemption.code.rule"].create(
            {"exemption_code_id": self.exemption_code.id, "state": "done"}
        )
        with self.assertRaises(UserError):
            rule.cancel_exemption_rule()

    def test_enable_rule_wrong_state(self):
        rule = self.env["exemption.code.rule"].create(
            {"exemption_code_id": self.exemption_code.id, "state": "draft"}
        )
        with self.assertRaises(UserError):
            rule.enable_exemption_rule()

    def test_cancel_failed_job_no_job(self):
        rule = self.env["exemption.code.rule"].create(
            {"exemption_code_id": self.exemption_code.id, "state": "progress"}
        )
        rule.cancel_exemption_rule_failed()
        self.assertEqual(rule.state, "cancel")


@tagged("-at_install", "post_install")
class TestResPartnerExemption(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Exemption Partner",
                "is_company": True,
                "street": "255 Executive Park Blvd",
                "city": "San Francisco",
                "state_id": cls.env.ref("base.state_us_5").id,
                "country_id": cls.env.ref("base.us").id,
                "zip": "94134",
            }
        )
        cls.exemption = cls.env["res.partner.exemption"].create(
            {"partner_id": cls.partner.id}
        )

    def test_export_no_config(self):
        with self.assertRaises(UserError):
            self.exemption.export_exemption()

    def test_cancel_from_draft_raises(self):
        with self.assertRaises(UserError):
            self.exemption.cancel_exemption()

    def test_cancel_from_progress_sets_cancel(self):
        self.env["avalara.salestax"].create(
            {
                "account_number": "TEST",
                "license_key": "TEST",
                "exemption_export": True,
            }
        )
        self.exemption.state = "progress"
        self.exemption.cancel_exemption()
        self.assertEqual(self.exemption.state, "cancel")

    def test_enable_from_draft_raises(self):
        with self.assertRaises(UserError):
            self.exemption.enable_exemption()

    def test_enable_no_config(self):
        self.exemption.state = "cancel"
        with self.assertRaises(UserError):
            self.exemption.enable_exemption()
