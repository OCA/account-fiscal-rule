# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule_sale for OpenERP
#   Copyright (C) 2009 Akretion <http://www.akretion.com>
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
#     @author Raphaël Valyi <raphael.valyi@akretion.com>
#   Copyright 2012 Camptocamp SA
#     @author: Guewen Baconnier
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

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _fiscal_position_map(
        self, result, partner_id=None, partner_invoice_id=None,
        partner_shipping_id=None, company_id=None
    ):
        fp_rule = self.env['account.fiscal.position.rule'].with_context(
            use_domain=('use_sale', '=', True)
        )
        return fp_rule.apply_fiscal_mapping(
            result, company_id=company_id,
        )

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        result = super(SaleOrder, self).onchange_partner_id(
            cr, uid, ids, partner_id, context=context)

        values = result['value']
        return self._fiscal_position_map(
            cr, uid,
            result,
            partner_id,
            values.get('partner_invoice_id', False),
            values.get('partner_shipping_id', False),
            context=context
        )

    def onchange_address_id(self, cr, uid, ids, partner_invoice_id,
                            partner_shipping_id, partner_id,
                            context=None):
        result = {'value': {}}
        if not partner_invoice_id:
            return result

        return self._fiscal_position_map(
            cr, uid, result,
            partner_id,
            partner_invoice_id,
            partner_shipping_id,
            context=context
        )
