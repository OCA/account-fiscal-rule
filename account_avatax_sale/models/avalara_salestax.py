from odoo import fields, models


class AvalaraSalestax(models.Model):
    _inherit = "avalara.salestax"

    use_partner_invoice_id = fields.Boolean(
        "Use Invoice partner's customer code in SO",
    )
