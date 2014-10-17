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

    @api.multi
    def onchange_partner_id(self, cr, uid, ids, partner_id, company_id):
        result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        # TODO waiting migration super method to new api
        partner_invoice_id = self.pool.get('res.partner').address_get(
            cr, uid, [partner_id], ['invoice'])['invoice']
        partner_shipping_id = self.pool.get('res.partner').address_get(
            cr, uid, [partner_id], ['delivery'])['delivery']

        kwargs = {
            'partner_id': partner_id,
            'partner_invoice_id': partner_invoice_id,
            'partner_shipping_id': partner_shipping_id,
            'company_id': company_id,
        }
        return self._fiscal_position_map(result, **kwargs)

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type,
                         journal_id, context=None):
        result = super(StockPicking, self)._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context)
        result['fiscal_position'] = picking.fiscal_position and \
            picking.fiscal_position.id
        return result
