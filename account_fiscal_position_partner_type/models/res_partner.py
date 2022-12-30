# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fiscal_position_type = fields.Selection(
        selection="_selection_fiscal_position_type",
        default=lambda self: self.env.company.default_fiscal_position_type,
    )

    def _selection_fiscal_position_type(self):
        field = "fiscal_position_type"
        return self.env["account.fiscal.position"].fields_get(allfields=[field])[field][
            "selection"
        ]

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ["fiscal_position_type"]
