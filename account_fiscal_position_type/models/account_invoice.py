# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fiscal_position_id = fields.Many2one(
        domain="[('type_position_use', 'in', {"
        "'out_invoice': ['sale', 'all'],"
        "'out_refund': ['sale', 'all'],"
        "'in_refund': ['purchase', 'all'],"
        "'in_invoice': ['purchase', 'all']}"
        ".get(type, []))]")

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        AccountFiscalPosition = self.env['account.fiscal.position']
        res = super(AccountInvoice, self)._onchange_partner_id()
        res['domain'] = res.get('domain', {})

        # Update Domain
        domain = self._get_domain_fiscal_position_id()
        res['domain']['fiscal_position'] = str(domain)

        # clean current fiscal position if it doesn't match the domain
        fiscal_position = self.fiscal_position_id
        if not fiscal_position:
            return res
        allow_fiscal_position_ids = AccountFiscalPosition.search(domain)
        if fiscal_position.id not in allow_fiscal_position_ids.ids:
            self.fiscal_position_id = False

        return res

    @api.multi
    def _get_domain_fiscal_position_id(self):
        self.ensure_one()
        if self.type in ['out_invoice', 'out_refund']:
            return [('type_position_use', 'in', ['sale', 'all'])]
        elif self.type in ['in_invoice', 'in_refund']:
            return [('type_position_use', 'in', ['purchase', 'all'])]
