#   Copyright (c) 2024 Groupe Voltaire
#   @author Emilie SOUTIRAS  <emilie.soutiras@groupevoltaire.com>
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_avatax_configuration = fields.Boolean(
        string="Active Avatax for this company",
        related="company_id.allow_avatax_configuration",
        readonly=False,
    )
