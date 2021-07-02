# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.tests import Form

class TestAccountFiscalPositionPartnerDomain(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountFiscalPositionPartnerDomain, cls).setUpClass()

        # MODELS
        cls.fiscal_position_model = cls.env["account.fiscal.position"]


        # INSTANCES
        # countries
        cls.country_us = cls.env.ref("base.us")

        # Company
        cls.company_main = cls.env.ref("base.main_company")
        cls.company_main.country_id=cls.country_us

        # Partners
        cls.partner_01 = cls.env.ref("base.res_partner_1") #zip=95380
        cls.partner_01.fiscal_position_id=False
        cls.partner_02 = cls.env.ref("base.res_partner_2")


        #taxes
        tax_group = cls.env['account.tax.group'].create({'name': 'Taxes_test'})
        cls.tax17 = cls.env['account.tax'].create({'name': 'Tax 17%', 'amount': 17, 'type_tax_use': 'sale','tax_group_id': tax_group.id})
        cls.tax15 = cls.env['account.tax'].create({'name': 'Tax 15%', 'amount': 15,  'type_tax_use': 'sale','tax_group_id': tax_group.id})


        # Fiscal positions
        cls.fpos = cls.env['account.fiscal.position'].create(
            {"name": "Tax 17", "partner_domain": '[["zip", "=", "95380"]]','auto_apply': True, })

        cls.env['account.fiscal.position.tax'].create({
            'position_id': cls.fpos.id,
            'tax_src_id': cls.tax15.id,
            'tax_dest_id': cls.tax17.id,
        })

        #products
        cls.product1 = cls.env['product.product'].create({
            'name': 'Product 1',
            'lst_price':100.00,
            'standard_price':100.00,
            'taxes_id': cls.tax15.ids,
            #'taxes_id': cls.tax15.ids,
        })


    def test_01(self):
        """
        Test case:
            - Assign invoice taxes based on partner domain
        Expected result:
            - Taxes correctly assigned
        """

        #invoice1 --> product tax is 15, invoice tax should be 17 (because customer zip code = 95380)

        move_form=Form(self.env['account.move'].with_context(
                default_type="out_invoice",))
        move_form.partner_id = self.partner_01
        with move_form.line_ids.new() as line_form:
            line_form.product_id=self.product1

        self.invoice1 = move_form.save()
        self.invoice1._onchange_partner_id()

        self.assertRecordValues(self.invoice1.line_ids.filtered('tax_line_id'), [
            {'name': self.tax17.name, 'tax_base_amount': 100, 'price_unit': 17.0, 'tax_ids': []},])


        # invoice2 --> product tax is 15, invoice tax should be 15 (because customer zip code != 95380)

        move_form2 = Form(self.env['account.move'].with_context(
            default_type="out_invoice", ))
        move_form2.partner_id = self.partner_02
        with move_form2.line_ids.new() as line_form:
            line_form.product_id = self.product1

        self.invoice2 = move_form2.save()
        self.assertRecordValues(self.invoice2.line_ids.filtered('tax_line_id'), [
            {'name': self.tax15.name, 'tax_base_amount': 100, 'price_unit': 15.0, 'tax_ids': []},

        ])



