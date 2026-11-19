# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMoveLineEcotax(models.Model):
    _name = "account.move.line.ecotax"
    _inherit = "ecotax.line.mixin"
    _description = "Account move line ecotax"

    account_move_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Journal Item",
        required=True,
        readonly=True,
        index=True,
        auto_join=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product",
        related="account_move_line_id.product_id",
        readonly=True,
        store=True,
    )
    quantity = fields.Float(
        related="account_move_line_id.quantity", readonly=True, store=True
    )
    currency_id = fields.Many2one(
        related="account_move_line_id.currency_id", readonly=True, store=True
    )

    def _is_frozen(self):
        """The ecotax amounts of a posted document are frozen: they are used
        to build the ecotax tax lines, the VAT computed on them and the
        ecotax collector reports.
        """
        return self.account_move_line_id.move_id.filtered(
            lambda move: move.state == "posted"
        )

    def _check_moves_not_frozen(self, moves):
        if moves.filtered(lambda move: move.state == "posted"):
            raise UserError(
                _("The ecotax lines of a posted document cannot be modified.")
            )

    @api.model_create_multi
    def create(self, vals_list):
        # only a parent already flushed can belong to a posted document: a
        # document being created or copied is a draft by definition, and its
        # lines are still NewId (not browsable, not readable)
        parents = self.env["account.move.line"].browse(
            [
                vals["account_move_line_id"]
                for vals in vals_list
                if isinstance(vals.get("account_move_line_id"), int)
            ]
        )
        self._check_moves_not_frozen(parents.move_id)
        return super().create(vals_list)

    def write(self, vals):
        # the view hides these fields but the RPC does not
        self._check_moves_not_frozen(self.account_move_line_id.move_id)
        return super().write(vals)

    def unlink(self):
        self._check_moves_not_frozen(self.account_move_line_id.move_id)
        return super().unlink()
