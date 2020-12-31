from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    avatax_id = fields.Char("Avatax Customer ID", copy=False, readonly=True)
    exemption_ids = fields.One2many(
        "res.partner.exemption", "partner_id", string="Avalara Exemptions"
    )
    use_commercial_entity = fields.Boolean(compute="_compute_use_commercial_entity")

    def _compute_use_commercial_entity(self):
        avalara_salestax = self.env["avalara.salestax"].sudo().search([], limit=1)
        for partner in self:
            partner.use_commercial_entity = avalara_salestax.use_commercial_entity
