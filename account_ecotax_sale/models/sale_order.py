# © 2015 -2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_ecotax = fields.Float(
        digits="Ecotaxe",
        string="Included Ecotaxe",
        store=True,
        compute="_compute_ecotax",
    )

    @api.depends("order_line.subtotal_ecotax")
    def _compute_ecotax(self):
        for order in self:
            order.amount_ecotax = sum(order.order_line.mapped("subtotal_ecotax"))
