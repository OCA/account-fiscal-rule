# © 2015 -2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    ecotax_line_ids = fields.One2many(
        "sale.order.line.ecotax",
        "sale_order_line_id",
        compute="_compute_ecotax_line_ids",
        store=True,
        readonly=False,
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
        unit = sum(self.ecotax_line_ids.mapped("amount_unit"))
        subtotal_ecotax = sum(self.ecotax_line_ids.mapped("amount_total"))
        return unit, subtotal_ecotax

    @api.depends(
        "currency_id",
        "ecotax_line_ids.amount_unit",
        "ecotax_line_ids.amount_total",
    )
    def _compute_ecotax(self):
        for line in self:
            amount_unit, subtotal = line._get_ecotax_amounts()
            line.subtotal_ecotax = subtotal
            line.ecotax_amount_unit = amount_unit

    def _get_new_vals_list(self):
        self.ensure_one()
        new_vals_list = [
            Command.create(
                {
                    "classification_id": ecotaxline_prod.classification_id.id,
                    "force_amount_unit": ecotaxline_prod.force_amount,
                }
            )
            for ecotaxline_prod in self.product_id.all_ecotax_line_product_ids
        ]
        return new_vals_list

    @api.depends("product_id")
    def _compute_ecotax_line_ids(self):
        """Unlink and recreate ecotax_lines when modifying the product_id."""
        for line in self:
            delete_vals_list = [
                Command.delete(taxline.id) for taxline in line.ecotax_line_ids
            ]
            new_vals_list = line._get_new_vals_list()
            update = new_vals_list + delete_vals_list
            line.ecotax_line_ids = update

    def edit_ecotax_lines(self):
        view = {
            "name": ("Ecotax classification"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sale.order.line",
            "view_id": self.env.ref(
                "account_ecotax_sale.view_sale_line_ecotax_form"
            ).id,
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
        }
        return view

    def _prepare_invoice_line(self, **optional_values):
        """Create equivalente ecotax_line_ids for account move line
        from sale order line ecotax_line_ids .
        """
        res = super()._prepare_invoice_line(**optional_values)
        ecotax_cls_vals = []
        for ecotaxline in self.ecotax_line_ids:
            ecotax_cls_vals.append(
                (
                    0,
                    0,
                    {
                        "classification_id": ecotaxline.classification_id.id,
                        "force_amount_unit": ecotaxline.force_amount_unit,
                    },
                )
            )
        res["ecotax_line_ids"] = ecotax_cls_vals
        return res
