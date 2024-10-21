from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    avatax_id = fields.Char("Avatax Customer ID", copy=False, readonly=True)
    exemption_ids = fields.One2many(
        "res.partner.exemption", "partner_id", string="Avalara Exemptions"
    )
