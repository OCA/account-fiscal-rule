# -*- coding: utf-8 -*-
# @ 2009 Akretion - www.akretion.com.br -
# @author Renato Lima <renato.lima@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        result = super(StockMove, self)._get_new_picking_values()

        result['fiscal_position_id'] = \
            self.procurement_id.sale_line_id.order_id.fiscal_position and \
            self.procurement_id.sale_line_id.order_id.fiscal_position.id
        return result


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Fiscal Position'
    )

    def _fiscal_position_map(self, **kwargs):
        ctx = dict(self.env.context)
        ctx.update({'use_domain': ('use_picking', '=', True)})
        return self.env['account.fiscal.position.rule'].with_context(
            ctx).apply_fiscal_mapping(**kwargs)

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        partner_address = self.partner_id.address_get(['invoice', 'delivery'])
        obj_partner_shipping = self.env['res.partner'].browse(
            partner_address.get('delivery')
        )
        obj_partner_invoice = self.env['res.partner'].browse(
            partner_address.get('invoice')
        )

        kwargs = {
            'company_id': self.company_id,
            'partner_id': self.partner_id,
            'partner_shipping_id': obj_partner_shipping,
            'partner_invoice_id': obj_partner_invoice,
        }
        obj_fiscal_position = self._fiscal_position_map(**kwargs)
        if obj_fiscal_position:
            self.fiscal_position_id = obj_fiscal_position.id

    @api.multi
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        inv_vals = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move
        )
        inv_vals.update({
            'fiscal_position_id': (move.picking_id.fiscal_position_id.id and
                                   move.picking_id.fiscal_position_id.id),
        })
        return inv_vals
