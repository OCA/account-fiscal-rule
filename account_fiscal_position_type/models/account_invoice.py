# coding: utf-8
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_domain_fiscal_position(self, type, partner_id):
        if type in ['out_invoice', 'out_refund']:
            return [('type_position_use', 'in', ['sale', 'all'])]
        elif type in ['in_invoice', 'in_refund']:
            return [('type_position_use', 'in', ['purchase', 'all'])]

    @api.multi
    def onchange_partner_id(
            self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        AccountFiscalPosition = self.env['account.fiscal.position']
        res = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if 'domain' not in res:
            res['domain'] = {}
        if 'value' not in res:
            res['value'] = {}

        domain = self._get_domain_fiscal_position(
            type, partner_id)
        res['domain']['fiscal_position'] = str(domain)

        fiscal_position_id = res['value'].get('fiscal_position', False)
        if not fiscal_position_id:
            return res

        allow_fiscal_position_ids = AccountFiscalPosition.search(domain)
        if fiscal_position_id not in allow_fiscal_position_ids.ids:
            res['value']['fiscal_position'] = False

        return res

    fiscal_position = fields.Many2one(
        domain="[('type_position_use', 'in', {"
        "'out_invoice': ['sale', 'all'],"
        "'out_refund': ['sale', 'all'],"
        "'in_refund': ['purchase', 'all'],"
        "'in_invoice': ['purchase', 'all']}"
        ".get(type, []))]")
