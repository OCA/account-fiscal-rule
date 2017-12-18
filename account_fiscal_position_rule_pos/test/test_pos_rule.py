# -*- coding: utf-8 -*-


from openerp.tests import common


class TestPOSRule(common.SavepointCase):

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestPOSRule, cls).setUpClass()
        cls.fp_model = cls.env['account.fiscal.position']
        cls.internal_fp = cls.fp_model.create({
            'name': 'Internal POS Sale',
            'auto_apply': True,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test POS Rule',
            'company_id': cls.env.ref('base.main_company').id,
            'property_account_position_id': cls.internal_fp.id,
        })
        # open a POS session
        cls.env.ref('point_of_sale.pos_config_main').open_session_cb()
        cls.pos_order = cls.env['pos.order'].create({
            'name': 'POS/ORD/1',
            'partner_id': cls.partner.id,
            'pricelist_id': cls.partner.property_product_pricelist.id,
            'product_id': cls.env.ref('product.product_product_3').id,
            'price_unit': 450,
            'discount': 5.0,
            'qty': 2,
        })

    def test_order_onchange(self):
        order = self.pos_order
        self.assertFalse(order.fiscal_position_id)
        order.onchange_fiscal_position_map()
        self.assertEqual(order.fiscal_position_id, self.internal_fp)
