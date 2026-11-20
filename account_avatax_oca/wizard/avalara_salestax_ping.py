from odoo import api, fields, models


class AvalaraSalestaxPing(models.TransientModel):
    _name = "avalara.salestax.ping"
    _description = "Ping Service"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        self.ping()
        return res

    name = fields.Char()

    @api.model
    def ping(self):
        """Call the AvaTax's Ping Service to test the connection."""
        active_id = self.env.context.get("active_id")
        if active_id:
            avatax = self.env["avalara.salestax"].browse(active_id)
            avatax.ping()
        return True
