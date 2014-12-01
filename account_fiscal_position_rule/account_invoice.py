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

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _fiscal_position_map(self, result, **kwargs):
        ctx = dict(self._context)
        ctx.update({'use_domain': ('use_invoice', '=', True)})
        return self.env['account.fiscal.position.rule'].with_context(
            ctx).apply_fiscal_mapping(result, **kwargs)

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):

        result = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice, payment_term,
            partner_bank_id, company_id)

        if not partner_id or not company_id:
            return result

        return self._fiscal_position_map(
            result, partner_id=partner_id, partner_invoice_id=partner_id,
            company_id=company_id)

    @api.multi
    def onchange_company_id(self, company_id, part_id, type,
                            invoice_line, currency_id):
        result = super(AccountInvoice, self).onchange_company_id(
            company_id, part_id, type, invoice_line,
            currency_id)

        if not part_id or not company_id:
            return result

        return self._fiscal_position_map(
            result, partner_id=part_id, partner_invoice_id=part_id,
            company_id=company_id)
