# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_fiscal_position_type = fields.Selection(
        selection=[("b2c", "Customer"), ("b2b", "Company")],
        string="Default Partner Fiscal Position Type",
    )
