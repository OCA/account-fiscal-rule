# -*- coding: utf-8 -*-
# @ 2019 Akretion - www.akretion.com.br -
#   Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestAccountFiscalPositionRuleSaleStock(common.TransactionCase):

    def setUp(self):
        super(TestAccountFiscalPositionRuleSaleStock, self).setUp()
        self.stock_picking_obj = self.env['stock.picking']
        self.invoice_model = self.env['account.invoice']
        self.stock_move = self.env['stock.move']
        self.stock_invoice_onshipping = self.env['stock.invoice.onshipping']
        self.stock_return_picking = self.env['stock.return.picking']
        self.fiscal_position = self.env['account.fiscal.position']

    def test_create_picking_based_procurement_fields(self):
        """Test create Picking based in Procurement fields"""

        # intial so
        self.partner = self.env.ref('base.res_partner_1')
        self.product = self.env.ref(
            'product.product_product_7_product_template')
        self.fiscal_position_test = self.fiscal_position.browse(
            self.ref(
                'account_fiscal_position_rule_stock.'
                'test_fiscal_position_stock'))
        so_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'fiscal_position_id': self.fiscal_position_test.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 5.0,
                'product_uom': self.product.uom_id.id,
                'price_unit': self.product.list_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        }
        self.so = self.env['sale.order'].create(so_vals)

        self.so.action_confirm()
        self.assertTrue(
            self.so.picking_ids,
            'Sale Stock: no picking created for "invoice on '
            'delivery" stockable products')

        self.assertEqual(
            self.so.invoice_status, 'no',
            'Sale Stock: so invoice_status should be "nothing to invoice"')

        pick = self.so.picking_ids

        self.assertTrue(
            pick.fiscal_position_id,
            'Get field Fiscal Position from Procurement failed.'
        )

        pick.invoice_state = '2binvoiced'
        for line in pick.move_lines:
            line.invoice_state = '2binvoiced'

        pick.action_confirm()
        pick.force_assign()
        pick.do_new_transfer()
        pick.action_done()

        wizard_obj = self.stock_invoice_onshipping.with_context(
            active_ids=[pick.id],
            active_model=pick._name,
            active_id=pick.id,
        ).create({
            'group': 'picking',
            'journal_type': 'sale'
        })
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        action = wizard.action_generate()
        domain = action.get('domain', [])
        invoice = self.invoice_model.search(domain)

        self.assertTrue(invoice, 'Invoice is not created.')
        for line in invoice.picking_ids:
            self.assertEquals(
                line.id, pick.id,
                'Relation between invoice and picking are missing.')
        for line in invoice.invoice_line_ids:
            self.assertTrue(
                line.invoice_line_tax_ids,
                'Taxes in invoice lines are missing.'
            )
        self.assertTrue(
            invoice.tax_line_ids, 'Total of Taxes in Invoice are missing.'
        )
        self.assertTrue(
            invoice.fiscal_position_id,
            'Mapping fiscal position on wizard to create invoice fail.'
        )
