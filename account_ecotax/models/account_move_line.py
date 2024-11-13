# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models


class AcountMoveLine(models.Model):
    _inherit = "account.move.line"

    ecotax_line_ids = fields.One2many(
        "account.move.line.ecotax",
        "account_move_line_id",
        string="Ecotax lines",
        copy=True,
    )
    subtotal_ecotax = fields.Float(
        string="Ecotax", digits="Ecotax", store=True, compute="_compute_ecotax"
    )
    ecotax_amount_unit = fields.Float(
        digits="Ecotax",
        string="Ecotax Unit",
        store=True,
        compute="_compute_ecotax",
    )

    def _get_ecotax_amounts(self):
        self.ensure_one()
        amount_unit = sum(self.ecotax_line_ids.mapped("amount_unit"))
        subtotal_ecotax = sum(self.ecotax_line_ids.mapped("amount_total"))
        return amount_unit, subtotal_ecotax

    @api.depends(
        "currency_id",
        "ecotax_line_ids.amount_unit",
        "ecotax_line_ids.amount_total",
    )
    def _compute_ecotax(self):
        for line in self:
            amount_unit, amount_total = line._get_ecotax_amounts()
            line.ecotax_amount_unit = amount_unit
            line.subtotal_ecotax = amount_total

    @api.onchange("product_id")
    def _onchange_product_ecotax_line(self):
        """Unlink and recreate ecotax_lines when modifying the product_id."""
        self.ecotax_line_ids.unlink()  # Remove all ecotax classification
        if self.product_id:
            self.ecotax_line_ids = [
                Command.create(
                    {
                        "classification_id": ecotaxline_prod.classification_id.id,
                        "force_amount_unit": ecotaxline_prod.force_amount,
                    }
                )
                for ecotaxline_prod in self.product_id.all_ecotax_line_product_ids
            ]

    def edit_ecotax_lines(self):
        view = {
            "name": ("Ecotax classification"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.move.line",
            "view_id": self.env.ref("account_ecotax.view_move_line_ecotax_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
        }
        return view
