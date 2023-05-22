# Copyright 2021 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends(
        "company_id.account_fiscal_country_id",
        "fiscal_position_id.country_id",
        "fiscal_position_id.foreign_vat",
    )
    def _compute_tax_country_id(self):
        oss_account_move_ids = self.filtered(
            lambda a: a.fiscal_position_id and a.fiscal_position_id.oss_oca
        )
        for record in oss_account_move_ids:
            record.tax_country_id = record.fiscal_position_id.country_id
        return super(AccountMove, self - oss_account_move_ids)._compute_tax_country_id()
