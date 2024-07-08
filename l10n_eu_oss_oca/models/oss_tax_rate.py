# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class OssTaxRate(models.Model):
    _name = "oss.tax.rate"
    _description = "oss tax rate"

    oss_country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country",
    )
    oss_state_ids = fields.Many2many(
        comodel_name="res.country.state",
        string="States",
    )
    general_rate = fields.Float(digits=(16, 4))
    reduced_rate = fields.Float(digits=(16, 4))
    superreduced_rate = fields.Float(string="Super Reduced Rate", digits=(16, 4))
    second_superreduced_rate = fields.Float(
        string="Second Super Reduced Rate", digits=(16, 4)
    )

    def get_rates_list(self):
        return [
            self.general_rate,
            self.reduced_rate,
            self.superreduced_rate,
            self.second_superreduced_rate,
        ]

    _sql_constraints = [
        (
            "oss_country_id_uniq",
            "unique(oss_country_id, general_rate)",
            "The Country must be unique !",
        ),
    ]
