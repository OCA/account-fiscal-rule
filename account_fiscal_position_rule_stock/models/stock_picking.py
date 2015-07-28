# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule_stock for OpenERP
#   Copyright (C) 2009 Akretion <http://www.akretion.com>
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
    _inherit = "stock.picking"

    fiscal_position = fields.Many2one(
        'account.fiscal.position',
        string='Fiscal Position',
        domain="[('fiscal_operation_id','=',fiscal_operation_id)]",
    )

    @api.model
    def _fiscal_position_map(
            self, result, partner_id=None, partner_invoice_id=None,
            partner_shipping_id=None, company_id=None
    ):
        fp_rule_obj = self.env['account.fiscal.position.rule'].with_context(
            use_domain=('use_picking', '=', True)
        )
        return fp_rule_obj.apply_fiscal_mapping(
            result,
            partner_id=partner_id,
            partner_invoice_id=partner_invoice_id,
            partner_shipping_id=partner_shipping_id,
            company_id=company_id,
        )

    def onchange_partner_in(self, cr, uid, ids, partner_id=None,
                            company_id=None, context=None):
        result = super(StockPicking, self).onchange_partner_in(
            cr, uid, partner_id, context
        )

        if not result:
            result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        address_data = self.pool["res.partner"].address_get(
            cr, uid, [partner_id], ['delivery', 'invoice']
        )
        return self._fiscal_position_map(
            cr, uid, result,
            partner_id=partner_id,
            partner_invoice_id=address_data['invoice'],
            partner_shipping_id=address_data['delivery'],
            company_id=company_id,
            context=context,
        )

    @api.model
    def _prepare_invoice(self, picking, partner, inv_type, journal_id):
        result = super(StockPicking, self)._prepare_invoice(
            picking, partner, inv_type, journal_id
        )
        if picking.fiscal_position:
                result['fiscal_position'] = picking.fiscal_position.id
        return result
