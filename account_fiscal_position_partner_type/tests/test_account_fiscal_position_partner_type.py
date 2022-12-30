# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import Form, common


class TestAccountFiscalPositionPartnerType(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # MODELS
        cls.res_partner_model = cls.env["res.partner"]
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        # INSTANCES
        # Company
        cls.company_main = cls.env.ref("base.main_company")
        cls.company_main.default_fiscal_position_type = "b2b"
        # Fiscal Positions
        cls.fiscal_position_test = cls.fiscal_position_model.create(
            {
                "name": "Test",
                "auto_apply": False,
                "fiscal_position_type": False,
                "sequence": 1,
            }
        )
        cls.fiscal_position_empty = cls.fiscal_position_model.create(
            {
                "name": "Empty",
                "auto_apply": True,
                "fiscal_position_type": False,
                "sequence": 2,
            }
        )
        cls.fiscal_position_b2c = cls.fiscal_position_model.create(
            {
                "name": "b2c",
                "auto_apply": True,
                "fiscal_position_type": "b2c",
                "sequence": 3,
            }
        )
        cls.fiscal_position_b2b = cls.fiscal_position_model.create(
            {
                "name": "b2b",
                "auto_apply": True,
                "fiscal_position_type": "b2b",
                "sequence": 4,
            }
        )
        # Partners
        cls.partner_01 = cls.env.ref("base.res_partner_1")
        cls.partner_01.write({"fiscal_position_type": False})
        cls.partner_02 = cls.env.ref("base.res_partner_2")
        cls.partner_02.write({"fiscal_position_type": "b2c"})
        cls.partner_03 = cls.env.ref("base.res_partner_3")
        cls.partner_03.write({"fiscal_position_type": "b2b"})
        cls.partner_04 = cls.env.ref("base.res_partner_4")
        cls.partner_04.write(
            {
                "fiscal_position_type": "b2b",
                "property_account_position_id": cls.fiscal_position_test.id,
            }
        )
        cls.partner_05 = cls.env.ref("base.res_partner_10")
        cls.partner_05.write({"fiscal_position_type": "b2b"})

    def _invoice_sale_create(self, partner):
        invoice_form = Form(
            self.env["account.move"].with_context(
                default_move_type="out_invoice", default_company_id=self.company_main.id
            )
        )
        invoice_form.invoice_date = fields.Date.today()
        invoice_form.partner_id = partner
        invoice = invoice_form.save()

        invoice._onchange_partner_id()
        return invoice

    def test_01(self):
        partner_id = self.res_partner_model.create({"name": "fiscal position test"})
        self.assertEqual(partner_id.fiscal_position_type, "b2b")
        fiscal_position_id = self.fiscal_position_model.create(
            {"name": "fiscal position test", "auto_apply": True}
        )
        self.assertEqual(fiscal_position_id.fiscal_position_type, "b2b")

    def test_02(self):
        invoice_01 = self._invoice_sale_create(self.partner_01)
        self.assertEqual(invoice_01.fiscal_position_id, self.fiscal_position_empty)
        invoice_02 = self._invoice_sale_create(self.partner_02)
        self.assertEqual(invoice_02.fiscal_position_id, self.fiscal_position_b2c)
        invoice_03 = self._invoice_sale_create(self.partner_03)
        self.assertEqual(invoice_03.fiscal_position_id, self.fiscal_position_b2b)
        invoice_04 = self._invoice_sale_create(self.partner_04)
        self.assertEqual(invoice_04.fiscal_position_id, self.fiscal_position_test)

    def test_03(self):
        fiscal_position_b2b_country = self.fiscal_position_model.create(
            {
                "name": "b2b with country",
                "auto_apply": True,
                "fiscal_position_type": "b2b",
                "country_id": self.env.ref("base.us").id,
            }
        )
        invoice_05 = self._invoice_sale_create(self.partner_05)
        self.assertEqual(invoice_05.fiscal_position_id, fiscal_position_b2b_country)
