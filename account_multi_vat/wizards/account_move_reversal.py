# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res.update(
            {
                "customer_vat_partner_id": move.customer_vat_partner_id.id,
                "customer_vat": move.customer_vat,
            }
        )
        return res
