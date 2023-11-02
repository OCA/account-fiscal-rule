from odoo import api, models


class AccountFiscalPosition(models.Model):

    _inherit = "account.fiscal.position"

    @api.constrains("country_id", "state_ids", "foreign_vat")
    def _validate_foreign_vat_country(self):
        for record in self:
            try:
                super()._validate_foreign_vat_country()
            except Exception:
                similar_fpos_domain = [
                    ("foreign_vat", "!=", False),
                    ("country_id", "=", record.country_id.id),
                    ("company_id", "=", record.company_id.id),
                    ("id", "!=", record.id),
                ]
                if record.state_ids:
                    similar_fpos_domain.append(
                        ("state_ids", "in", record.state_ids.ids)
                    )

                similar_fpos_count = self.env["account.fiscal.position"].search_count(
                    similar_fpos_domain
                )
                if similar_fpos_count:
                    pass
        return True
