# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2025 Kencove (https://www.kencove.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestACcountAvataxExemptionSignOca(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.exemption_model = cls.env["res.partner.exemption"]
        cls.sign_oca_request_model = cls.env["sign.oca.request"]
        cls.sign_oca_template_model = cls.env["sign.oca.template"]
        cls.sign_oca_exemption_type_model = cls.env["res.partner.exemption.type"]
        cls.partner_model = cls.env["res.partner"]
        cls.avalara_salestax_model = cls.env["avalara.salestax"]
        cls.sign_oca_field_model = cls.env["sign.oca.field"]

        cls.partner = cls.partner_model.create(
            {
                "name": "Test Partner",
            }
        )
        cls.sign_oca_exemption_type = cls.sign_oca_exemption_type_model.create(
            {
                "name": "Test Exemption Type",
                "state_ids": [Command.set(cls.env.ref("base.state_us_1").ids)],
            }
        )
        cls.sign_oca_template = cls.sign_oca_template_model.create(
            {
                "name": "Test Sign Template",
                "data": "Test",
                "filename": "empty.pdf",
                "is_exemption": True,
                "exemption_type": cls.sign_oca_exemption_type.id,
            }
        )
        cls.sign_oca_field = cls.sign_oca_field_model.search(
            [("name", "=", "Tax Exemption Number")], limit=1
        )
        cls.sign_oca_template.item_ids.create(
            {
                "template_id": cls.sign_oca_template.id,
                "role_id": cls.env.ref("sign_oca.sign_role_customer").id,
                "page": 1,
                "position_x": 10,
                "position_y": 10,
                "width": 10,
                "height": 10,
                "required": True,
                "field_id": cls.sign_oca_field.id,
            }
        )
        cls.sign_oca_request = cls.sign_oca_request_model.create(
            {
                "name": "Test Sign Request",
                "template_id": cls.sign_oca_template.id,
                "signatory_data": cls.sign_oca_template._get_signatory_data(),
                "data": "Test",
                "signer_ids": [
                    Command.create(
                        {
                            "partner_id": cls.partner.id,
                            "role_id": cls.env.ref("sign_oca.sign_role_customer").id,
                        },
                    )
                ],
            }
        )
        cls.exemption = cls.exemption_model.create(
            {
                "name": "Test Exemption",
                "partner_id": cls.partner.id,
                "state": "draft",
                "sign_oca_request_id": cls.sign_oca_request.id,
                "exemption_number": "12345",
            }
        )
        cls.avalara_salestax = cls.avalara_salestax_model.create(
            {
                "account_number": "12345",
                "license_key": "12345",
                "exemption_export": True,
                "exemption_rule_export": True,
                "use_commercial_entity": True,
                "company_code": "TEST",
            }
        )

    def test_01_check_exemption_and_sign_oca_request(self):
        self.assertTrue(self.sign_oca_request.is_exemption)
        self.assertIn(self.exemption, self.sign_oca_request.exemption_ids)
        self.assertEqual(self.exemption.sign_oca_request_id, self.sign_oca_request)
        self.assertEqual(self.exemption.state, "draft")

    def test_02_test_cancel_sign_request_id(self):
        self.assertEqual(self.exemption.state, "draft")
        self.assertEqual(self.exemption.sign_oca_request_id.state, "1_draft")
        self.exemption.write({"state": "cancel"})
        self.exemption._cancel_sign_request_id()
        self.assertEqual(self.exemption.state, "cancel")
        self.assertEqual(self.exemption.sign_oca_request_id.state, "3_cancel")

    def test_03_get_partner_id(self):
        partner_id = self.sign_oca_request._get_partner_id()
        self.assertEqual(
            partner_id, self.partner, "The partner ID should match the created partner"
        )

    def test_04_prepare_exemption_data(self):
        self.sign_oca_request.state = "2_signed"
        exemption_data = self.sign_oca_request._prepare_exemption_data()
        self.assertIn("partner_id", exemption_data)
        self.assertIn("exemption_type", exemption_data)
        self.assertIn("sign_oca_request_id", exemption_data)

    def test_05_check_signed(self):
        self.sign_oca_request.state = "2_signed"
        self.sign_oca_request.is_exemption = True
        signatory_data = self.sign_oca_request.signatory_data
        next(
            item.update({"value": "12345"})
            for item in signatory_data.values()
            if item.get("name") == "Tax Exemption Number"
        )
        self.sign_oca_request.write({"signatory_data": signatory_data})
        self.sign_oca_request._check_signed()
        exemption = self.env["res.partner.exemption"].search(
            [("sign_oca_request_id", "=", self.sign_oca_request.id)], limit=1
        )

        self.assertEqual(exemption.exemption_number, "12345")
        self.assertEqual(exemption.state, "draft")
        self.assertEqual(exemption.exemption_validity_duration, 30)
        self.assertEqual(exemption.sign_oca_request_id.state, "2_signed")

    def test_06_open_exemptions(self):
        action = self.sign_oca_request.open_exemptions()
        self.assertEqual(action["res_model"], "res.partner.exemption")
        self.assertEqual(action["view_mode"], "list,form")
        self.assertIn(
            ("sign_oca_request_id", "=", self.sign_oca_request.id), action["domain"]
        )
