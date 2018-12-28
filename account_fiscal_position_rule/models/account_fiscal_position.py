# -*- coding: utf-8 -*-
# Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#   @author Renato Lima <renato.lima@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    @api.model
    def get_fiscal_position(self, partner_id, delivery_id=None):
        fp = super(AccountFiscalPosition, self).get_fiscal_position(
            partner_id, delivery_id)

        if not fp and partner_id and delivery_id:
            fiscal_rule = self.env['account.fiscal.position.rule']
            kwargs = {
                'company_id': self.env.user.company_id,
                'partner_id': self.env['res.partner'].browse(partner_id),
                'partner_invoice_id': self.env['res.partner'].browse(partner_id),
                'partner_shipping_id': self.env['res.partner'].browse(delivery_id)
            }

            fp = fiscal_rule.with_context(ctx).apply_fiscal_mapping(**kwargs)

        return fp.id or False
