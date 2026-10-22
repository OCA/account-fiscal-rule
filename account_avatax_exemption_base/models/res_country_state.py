from odoo import fields, models


class CountryState(models.Model):
    _inherit = "res.country.state"

    avatax_code = fields.Char(copy=False)
    avatax_name = fields.Char(copy=False)
    avatax_nexus = fields.Boolean(copy=False)
