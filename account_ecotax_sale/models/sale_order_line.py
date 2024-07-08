# © 2015 -2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    ecotax_line_ids = fields.One2many(
        "sale.order.line.ecotax",
        "sale_order_line_id",
        string="Ecotaxe lines",
        copy=True,
    )
    subtotal_ecotax = fields.Float(
        digits="Ecotaxe", store=True, compute="_compute_ecotax"
    )
    ecotax_amount_unit = fields.Float(
        digits="Ecotaxe",
        string="ecotax Unit.",
        store=True,
        compute="_compute_ecotax",
    )

    @api.depends(
        "order_id.currency_id",
        "tax_id",
    )
    def _compute_ecotax(self):
        for line in self:
            ecotax_ids = line.tax_id.filtered(lambda tax: tax.is_ecotax)
            if (line.display_type and line.display_type != "product") or not ecotax_ids:
                continue
            amount_currency = line.price_unit * (1 - line.discount / 100)
            quantity = line.product_uom_qty
            compute_all_currency = ecotax_ids.compute_all(
                amount_currency,
                currency=line.currency_id,
                quantity=quantity,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )
            subtotal_ecotax = 0.0
            for tax in compute_all_currency["taxes"]:
                subtotal_ecotax += tax["amount"]

            unit = quantity and subtotal_ecotax / quantity or subtotal_ecotax
            line.ecotax_amount_unit = unit
            line.subtotal_ecotax = subtotal_ecotax

    @api.depends("product_id", "company_id")
    def _compute_tax_id(self):
        res = super()._compute_tax_id()
        for line in self:
            line.tax_id |= line._get_computed_ecotaxes()
        return res

    def _get_computed_ecotaxes(self):
        self.ensure_one()
        sale_ecotaxes = self.product_id.all_ecotax_line_product_ids.mapped(
            "classification_id"
        ).mapped("sale_ecotax_ids")
        ecotax_ids = sale_ecotaxes.filtered(
            lambda tax: tax.company_id == self.order_id.company_id
        )

        if ecotax_ids and self.order_id.fiscal_position_id:
            ecotax_ids = self.order_id.fiscal_position_id.map_tax(ecotax_ids)
        return ecotax_ids

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
            "name": ("Ecotaxe classification"),
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
        if self.ecotax_line_ids:
            res["ecotax_line_ids"] = [
                Command.create(
                    {
                        "classification_id": ecotaxline.classification_id.id,
                        "force_amount_unit": ecotaxline.force_amount_unit,
                    }
                )
                for ecotaxline in self.ecotax_line_ids
            ]
        return res
