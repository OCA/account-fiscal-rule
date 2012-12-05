# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule for OpenERP
#   Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
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

from osv import fields, osv


class account_invoice(osv.osv):

    _inherit = 'account.invoice'

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):

        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)

        if not partner_id or not company_id or not result['value']['address_invoice_id']:
            return result

        partner_invoice_id = result['value'].get('partner_invoice_id', False)
        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        fiscal_result = obj_fiscal_position_rule.fiscal_position_map(cr, uid,  partner_id, partner_invoice_id, company_id, context={'use_domain': ('use_invoice', '=', True)})

        result['value'].update(fiscal_result)

        return result

    def onchange_company_id(self, cr, uid, ids, company_id, part_id, type, invoice_line, currency_id):
        result = super(account_invoice, self).onchange_company_id(cr, uid, ids, company_id, part_id, type, invoice_line, currency_id)

        if not part_id or not company_id or not ptn_invoice_id:
            return result

        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        fiscal_result = obj_fiscal_position_rule.fiscal_position_map(cr, uid, part_id, ptn_invoice_id, company_id, context={'use_domain': ('use_invoice', '=', True)})

        result['value'].update(fiscal_result)

        return result

    def onchange_address_id(self, cr, uid, ids, cpy_id, ptn_id, ptn_invoice_id=None, ptn_shipping_id=None):

        result = {'value': {'fiscal_position': False}}

        if not ptn_id or not cpy_id or not ptn_invoice_id:
            return result

        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        fiscal_result = obj_fiscal_position_rule.fiscal_position_map(cr, uid, ptn_id, ptn_invoice_id, ptn_shipping_id, cpy_id, context={'use_domain': ('use_invoice', '=', True)})

        result['value'].update(fiscal_result)

        return result

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
