from odoo import fields, models


class CountryState(models.Model):
    _inherit = "res.country.state"

    rule_ids = fields.One2many("exemption.code.rule", "state_id", "Avatax Rules")
