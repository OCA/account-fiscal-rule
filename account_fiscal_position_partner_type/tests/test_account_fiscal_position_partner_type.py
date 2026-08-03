# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestAccountFiscalPositionPartnerType(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # MODELS
        cls.res_partner_model = cls.env["res.partner"]
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        cls.res_partner_category_model = cls.env["res.partner.category"]
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
        # Accountability
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "TEST",
                "account_type": "income",
                "company_ids": [(6, 0, [cls.company_main.id])],
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test Journal",
                "type": "sale",
                "code": "TEST",
                "company_id": cls.company_main.id,
                "default_account_id": cls.account.id,
            }
        )
        # Partner Categories
        cls.category_00 = cls.res_partner_category_model.create(
            {"name": "Vendor", "color": 2}
        )
        cls.category_08 = cls.res_partner_category_model.create(
            {"name": "Consulting Services", "color": 5}
        )
        cls.category_12 = cls.res_partner_category_model.create(
            {"name": "Office Supplies", "parent_id": cls.category_00.id, "color": 8}
        )
        cls.category_14 = cls.res_partner_category_model.create(
            {"name": "Desk Manufacturers", "parent_id": cls.category_00.id, "color": 10}
        )
        # Partners
        cls.partner_01 = cls.res_partner_model.create(
            {
                "name": "Wood Corner",
                "category_id": [cls.category_12.id, cls.category_14.id],
                "is_company": True,
                "street": "1839 Arbor Way",
                "city": "Turlock",
                "state_id": cls.env.ref("base.state_us_5").id,
                "zip": 95380,
                "country_id": cls.env.ref("base.us").id,
                "email": "wood.corner26@example.com",
                "phone": "(623)-853-7197",
                "website": "http://www.wood-corner.com",
                "vat": "US12345672",
                "property_account_receivable_id": cls.account.id,
            }
        )
        cls.partner_01.write({"fiscal_position_type": False})
        cls.partner_02 = cls.res_partner_model.create(
            {
                "name": "Acme Corporation",
                "category_id": [cls.category_14.id],
                "is_company": True,
                "street": "77 Santa Barbara Rd",
                "city": "Pleasant Hill",
                "state_id": cls.env.ref("base.state_us_5").id,
                "zip": 94523,
                "country_id": cls.env.ref("base.us").id,
                "email": "acme_corp@yourcompany.example.com",
                "phone": "(603)-996-3829",
                "website": "http://www.acme-example-company.com",
                "vat": "US12345673",
                "property_account_receivable_id": cls.account.id,
            }
        )
        cls.partner_02.write({"fiscal_position_type": "b2c"})
        cls.partner_03 = cls.res_partner_model.create(
            {
                "name": "Gemini Furniture",
                "category_id": [cls.category_08.id, cls.category_14.id],
                "is_company": True,
                "street": "Via Industria 21",
                "city": "Serravalle",
                "zip": 47899,
                "country_id": cls.env.ref("base.sm").id,
                "email": "gemini_furniture@fake.geminifurniture.com",
                "phone": "+378 0549 885555",
                "website": "http://www.gemini-furniture.com",
                "vat": "SM12345",
                "property_account_receivable_id": cls.account.id,
            }
        )
        cls.partner_03.write({"fiscal_position_type": "b2b"})
        cls.partner_04 = cls.res_partner_model.create(
            {
                "name": "Ready Mat",
                "category_id": [cls.category_12.id, cls.category_14.id],
                "is_company": True,
                "street": "7500 W Linne Road",
                "city": "Tracy",
                "state_id": cls.env.ref("base.state_us_5").id,
                "zip": 95304,
                "country_id": cls.env.ref("base.us").id,
                "email": "ready.mat28@example.es",
                "phone": "(803)-873-6126",
                "website": "http://www.ready-mat.com",
                "vat": "US12345675",
                "property_account_receivable_id": cls.account.id,
            }
        )
        cls.partner_04.write(
            {
                "fiscal_position_type": "b2b",
                "property_account_position_id": cls.fiscal_position_test.id,
            }
        )
        cls.partner_05 = cls.res_partner_model.create(
            {
                "name": "The Jackson Group",
                "is_company": True,
                "street": "1611 Peony Dr",
                "city": "Tracy",
                "state_id": cls.env.ref("base.state_us_5").id,
                "zip": 95377,
                "country_id": cls.env.ref("base.us").id,
                "email": "jackson.group82@example.com",
                "phone": "(334)-502-1024",
                "vat": "US12345676",
                "property_account_receivable_id": cls.account.id,
            }
        )
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
