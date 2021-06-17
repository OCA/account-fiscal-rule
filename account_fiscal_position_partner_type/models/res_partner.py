# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fiscal_position_type = fields.Selection(
        selection=[("b2c", "Customer"), ("b2b", "Company")],
        string="Fiscal Position Type",
        default=lambda self: self._default_fiscal_position_type(),
    )

    @api.model
    def _default_fiscal_position_type(self):
        fiscal_position_type = None
        if self.env['res.company']._company_default_get():
            fiscal_position_type = self.env[
                'res.company']._company_default_get(
                    )[0].default_fiscal_position_type
        return fiscal_position_type

    @api.model
    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + ["fiscal_position_type"]
