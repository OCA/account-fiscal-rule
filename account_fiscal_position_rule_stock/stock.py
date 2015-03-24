# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule_stock for OpenERP
#   Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fiscal_position = fields.Many2one(
        'account.fiscal.position', 'Fiscal Position',
        domain="[('fiscal_operation_id','=',fiscal_operation_id)]")

    def _fiscal_position_map(self, result, **kwargs):
        ctx = dict(self._context)
        ctx.update({'use_domain': ('use_picking', '=', True)})
        return self.env['account.fiscal.position.rule'].with_context(
            ctx).apply_fiscal_mapping(result, **kwargs)

    @api.onchange('partner_id')
    def onchange_partner_id(self, **kwargs):
        result = {'value': {'fiscal_position': False}}

        if not self.partner_id or not self.company_id:
            return result

        partner_address = self.partner_id.address_get(
            ['invoice', 'delivery'])

        kwargs.update({
            'partner_id': self.partner_id.id,
            'partner_invoice_id': partner_address['invoice'],
            'partner_shipping_id': partner_address['delivery'],
            'company_id': self.company_id.id,
        })
        result = self.update(
            self._fiscal_position_map(result, **kwargs)['value'])

    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move,
                          context=None):
        inv_vals = super(StockPicking, self)._get_invoice_vals(
            cr, uid, key, inv_type, journal_id, move, context=context)
        inv_vals.update({
            'fiscal_position': (move.picking_id.fiscal_position and
                                move.picking_id.fiscal_position.id),
            })
        return inv_vals
