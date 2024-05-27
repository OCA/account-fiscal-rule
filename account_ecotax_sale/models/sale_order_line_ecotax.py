# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLineEcotaxe(models.Model):
    _name = "sale.order.line.ecotax"
    _inherit = "ecotax.line.mixin"
    _description = "Sale order line ecotax"

    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale line",
        required=True,
        readonly=True,
        index=True,
        auto_join=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product", related="sale_order_line_id.product_id", readonly=True
    )
    quantity = fields.Float(related="sale_order_line_id.product_uom_qty", readonly=True)
    currency_id = fields.Many2one(
        related="sale_order_line_id.currency_id", readonly=True
    )
