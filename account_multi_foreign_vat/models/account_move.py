# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains("line_ids", "fiscal_position_id", "company_id")
    def _validate_taxes_country(self):
        filtered_self = self.browse()
        for record in self:
            amls = record.line_ids
            impacted_countries = amls.tax_ids.country_id | amls.tax_line_id.country_id
            if record.fiscal_position_id.country_group_id and all(
                ic in record.fiscal_position_id.country_group_id.country_ids
                for ic in impacted_countries
            ):
                continue
            if (
                not record.fiscal_position_id.country_group_id
                and not record.fiscal_position_id.country_id
            ):
                continue
            filtered_self |= record

        return super(AccountMove, filtered_self)._validate_taxes_country()
