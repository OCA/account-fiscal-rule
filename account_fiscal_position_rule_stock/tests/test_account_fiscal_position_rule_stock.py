# -*- coding: utf-8 -*-
# @ 2019 Akretion - www.akretion.com.br -
#   Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestAccountFiscalPositionRuleStock(common.TransactionCase):

    def setUp(self):
        super(TestAccountFiscalPositionRuleStock, self).setUp()
        self.stock_picking_obj = self.env['stock.picking']
        self.stock_invoice_onshipping = self.env['stock.invoice.onshipping']
        self.stock_return_picking = self.env['stock.return.picking']
        self.stock_picking_1 = self.stock_picking_obj.browse(
            self.ref(
                'account_fiscal_position_rule_stock.'
                'test_fiscal_position_rule_stock_1')
        )
        self.stock_picking_2 = self.stock_picking_obj.browse(
            self.ref(
                'account_fiscal_position_rule_stock.'
                'test_fiscal_position_rule_stock_2')
        )
        self.stock_picking_3 = self.stock_picking_obj.create(dict(
            partner_id=self.env.ref('base.res_partner_12').id,
            picking_type_id=self.env.ref('stock.picking_type_out').id,
            location_id=self.env.ref('stock.stock_location_stock').id,
            location_dest_id=self.env.ref('stock.stock_location_customers').id,
            invoice_state='2binvoiced',
            move_lines=[(0, 0, dict(
                name='Test - account_fiscal_position_rule_stock - 3',
                product_id=self.env.ref(
                    'product.product_product_7_product_template').id,
                product_uom_qty=2,
                product_uom=self.env.ref('product.product_uom_unit').id,
                location_id=self.env.ref('stock.stock_location_stock').id,
                location_dest_id=self.env.ref(
                    'stock.stock_location_customers').id,
                invoice_state='2binvoiced',
            ))]
        ))

    def test_onchange_partner(self):
        self.stock_picking_3.onchange_partner_id()
        self.assertTrue(
            self.stock_picking_3.fiscal_position_id,
            'Onchange on partner_id fail to mapping fiscal position.'
        )

    def test_create_invoice(self):
        wizard_group_partner = self.stock_invoice_onshipping.with_context(
            active_ids=[self.stock_picking_2.id]
        ).create({
            'group': False,
            'journal_type': 'sale'
        })
        wizard_group_partner.open_invoice()

        invoice = self.env['account.invoice'].search([(
            'origin', '=', self.stock_picking_2.name
        )])
        self.assertTrue(invoice, 'Invoice is not created.')
        for line in invoice.invoice_line_ids:
            self.assertEquals(
                line.picking_id.id, self.stock_picking_2.id,
                'Relation between invoice line and picking are missing.')
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
