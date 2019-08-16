# -*- coding: utf-8 -*-
# @ 2009 Akretion - www.akretion.com.br -
# @author Renato Lima <renato.lima@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Fiscal Position')

    def _fiscal_position_map(self, **kwargs):
        ctx = dict(self.env.context)
        ctx.update({'use_domain': ('use_picking', '=', True)})
        return self.env['account.fiscal.position.rule'].with_context(
            ctx).apply_fiscal_mapping(**kwargs)

    @api.multi
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
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
