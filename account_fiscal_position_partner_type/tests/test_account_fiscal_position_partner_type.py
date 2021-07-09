# -*- encoding: utf-8 -*-
# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import SavepointCase


class TestAccountFiscalPositionPartnerType(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountFiscalPositionPartnerType, cls).setUpClass()
        # MODELS
        cls.res_partner_model = cls.env["res.partner"]
        cls.account_invoice_model = cls.env["account.invoice"]
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
        cls.partner_01 = cls.res_partner_model.create({
            'name': 'Test partner 1',
            'fiscal_position_type': False
        })
        cls.partner_02 = cls.res_partner_model.create({
            'name': 'Test partner 2',
            'fiscal_position_type': 'b2c'
        })
        cls.partner_03 = cls.res_partner_model.create({
            'name': 'Test partner 3',
            'fiscal_position_type': 'b2b'
        })
        cls.partner_04 = cls.res_partner_model.create({
            'name': 'Test partner 4',
            'fiscal_position_type': 'b2b',
            'property_account_position': cls.fiscal_position_test.id,
        })
        cls.partner_05 = cls.res_partner_model.create({
            'name': 'Test partner 5',
            'fiscal_position_type': 'b2b',
            "country_id": cls.env.ref("base.us").id
        })

    @classmethod
    def _check_fiscal_position(cls, partner):
        res = cls.fiscal_position_model.get_fiscal_position(
            cls.company_main.id, partner.id)
        return res

    def test_01(self):
        partner_id = self.res_partner_model.create({"name": "fiscal position test"})
        self.assertEqual(partner_id.fiscal_position_type, "b2b")
        fiscal_position_id = self.fiscal_position_model.create(
            {"name": "fiscal position test", "auto_apply": True}
        )
        self.assertEqual(fiscal_position_id.fiscal_position_type, "b2b")

    def test_02(self):
        invoice_01 = self._check_fiscal_position(self.partner_01)
        self.assertEqual(invoice_01, self.fiscal_position_empty.id)
        invoice_02 = self._check_fiscal_position(self.partner_02)
        self.assertEqual(invoice_02, self.fiscal_position_b2c.id)
        invoice_03 = self._check_fiscal_position(self.partner_03)
        self.assertEqual(invoice_03, self.fiscal_position_b2b.id)
        invoice_04 = self._check_fiscal_position(self.partner_04)
        self.assertEqual(invoice_04, self.fiscal_position_test.id)

    def test_03(self):
        fiscal_position_b2b_country = self.fiscal_position_model.create(
            {
                "name": "b2b with country",
                "auto_apply": True,
                "fiscal_position_type": "b2b",
                "country_id": self.env.ref("base.us").id,
            }
        )
        invoice_05 = self._check_fiscal_position(self.partner_05)
        self.assertEqual(invoice_05, fiscal_position_b2b_country.id)
