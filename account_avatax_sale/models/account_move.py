from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        self._onchange_partner_shipping_id()
        return res

    @api.onchange("partner_shipping_id")
    def _onchange_partner_shipping_id(self):
        res = super(AccountMove, self)._onchange_partner_shipping_id()
        self.tax_on_shipping_address = bool(self.partner_shipping_id)
        return res
