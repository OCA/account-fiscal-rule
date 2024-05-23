# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLineEcotax(models.Model):
    _name = "account.move.line.ecotax"
    _inherit = "ecotax.line.mixin"
    _description = "Account move line ecotax"

    account_move_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Account move line",
        required=True,
        readonly=True,
        index=True,
        auto_join=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product", related="account_move_line_id.product_id", readonly=True
    )
    quantity = fields.Float(related="account_move_line_id.quantity", readonly=True)
    currency_id = fields.Many2one(
        related="account_move_line_id.currency_id", readonly=True
    )
