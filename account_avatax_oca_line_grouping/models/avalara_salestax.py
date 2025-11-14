from odoo import fields, models


class AvalaraSalestax(models.Model):
    _inherit = "avalara.salestax"

    avatax_group_lines = fields.Boolean(
        string="Group document lines for Avatax",
        related="company_id.avatax_group_lines",
        readonly=False,
        help=(
            "If enabled on the company, Avatax will receive a single aggregated "
            "line per document instead of one line per order/invoice line."
        ),
    )
