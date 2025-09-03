# Copyright 2025 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains("property_account_position_id")
    def check_fiscal_position_and_vies_valid(self):
        if not self.env.company.vat_check_vies:
            return
        for record in self:
            if (
                record.property_account_position_id.is_show_vies_warning
                and not record.vies_valid
            ):
                record.property_account_position_id.raise_vies_warning(record.name)
