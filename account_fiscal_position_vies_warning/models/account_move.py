# Copyright 2025 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        if not self.env.company.vat_check_vies:
            return super().action_post()
        for record in self:
            if (
                record.fiscal_position_id.is_show_vies_warning
                and not record.partner_id.vies_valid
            ):
                self.fiscal_position_id.raise_vies_warning(record.partner_id.name)
        return super().action_post()
