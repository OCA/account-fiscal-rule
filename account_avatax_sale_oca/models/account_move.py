from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_id", "partner_shipping_id")
    def _onchange_partner_shipping_id(self):
        for move in self:
            move.tax_on_shipping_address = bool(move.partner_shipping_id)
