# -*- coding: utf-8 -*-
# Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Renato Lima <renato.lima@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    #@api.onchange('partner_id', 'company_id')
    #def _onchange_partner_id(self):
    #    ctx = dict(self._context)
    #    ctx.update({'use_domain': ('use_invoice', '=', True)})
    #    self.with_context(ctx)
