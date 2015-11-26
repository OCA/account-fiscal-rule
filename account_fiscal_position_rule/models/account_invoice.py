# -*- coding: utf-8 -*-
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

    def _fiscal_position_map(self, **kwargs):
        ctx = dict(self._context)
        ctx.update({'use_domain': ('use_invoice', '=', True)})
        # print 'FISCAL POSITION MAP', kwargs
        return self.env['account.fiscal.position.rule'].with_context(
            ctx).apply_fiscal_mapping(**kwargs)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):

        super(AccountInvoice, self)._onchange_partner_id()

        if self.partner_id and self.company_id:
            kwargs = {
                'company_id': self.company_id,
                'partner_id': self.partner_id,
                'partner_invoice_id': self.partner_id,
                'partner_shipping_id': self.partner_id,
            }
            obj_fiscal_position = self._fiscal_position_map(**kwargs)
            if obj_fiscal_position is not False:
                self.fiscal_position_id = obj_fiscal_position.id
