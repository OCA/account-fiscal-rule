# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule_purchase for OpenERP
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

from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _fiscal_position_map(self, result, company_id, partner_id,
                             partner_invoice_id, partner_shipping_id,
                             ):
        fp_rule_obj = self.env['account.fiscal.position.rule'].with_context(
            use_domain=('use_purchase', '=', True)
        )

        return fp_rule_obj.apply_fiscal_mapping(
            result,
            company_id=company_id,
            partner_id=partner_id,
            partner_invoice_id=partner_invoice_id,
            partner_shipping_id=partner_shipping_id,
        )

    def onchange_partner_id(self, cr, uid, ids, partner_id, company_id=None,
                            context=None):
        result = super(PurchaseOrder, self).onchange_partner_id(
            cr, uid, ids, partner_id)

        if not partner_id or not company_id:
            return result

        return self._fiscal_position_map(
            cr, uid, result,
            company_id,
            partner_id,
            partner_id,
            partner_id,
            context=context
        )

    def onchange_dest_address_id(self, cr, uid, ids, partner_id,
                                 dest_address_id, company_id=None,
                                 context=None):
        result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        return self._fiscal_position_map(
            cr, uid, result,
            company_id,
            partner_id,
            partner_id,
            dest_address_id,
            context=context
        )

    @api.onchange('company_id')
    @api.depends('partner_id', 'dest_address_id')
    def onchange_company_id(self):
        result = {'value': {'fiscal_position': False}}

        if not self.partner_id or not self.company_id:
            return result

        return self._fiscal_position_map(
            result,
            company_id=self.company_id.id,
            partner_id=self.partner_id.id,
            partner_invoice_id=self.partner_id.id,
            partner_shipping_id=self.dest_address_id.id,
        )
