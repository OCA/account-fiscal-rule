# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        ctx = self.env.context.copy()
        ctx.update({"use_domain": ("use_invoice", "=", True)})
        return super(AccountMove, self.with_context(ctx))._onchange_partner_id()
