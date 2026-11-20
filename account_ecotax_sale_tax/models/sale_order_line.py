# © 2015 -2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    subtotal_ecotax = fields.Float(compute="_compute_ecotax_tax")
    ecotax_amount_unit = fields.Float(
        compute="_compute_ecotax_tax",
    )

    def _get_ecotax_amounts(self):
        self.ensure_one()
        # do not call super as we completly change the way to compute it
        ecotax_ids = self.tax_id.filtered(lambda tax: tax.is_ecotax)
        if (self.display_type and self.display_type != "product") or not ecotax_ids:
            return 0.0, 0.0
        amount_currency = self.price_unit * (1 - self.discount / 100)
        quantity = self.product_uom_qty
        compute_all_currency = ecotax_ids.compute_all(
            amount_currency,
            currency=self.currency_id,
            quantity=quantity,
            product=self.product_id,
            partner=self.order_id.partner_shipping_id,
        )
        subtotal_ecotax = 0.0
        for tax in compute_all_currency["taxes"]:
            subtotal_ecotax += tax["amount"]

        unit = quantity and subtotal_ecotax / quantity or subtotal_ecotax
        return unit, subtotal_ecotax

    @api.depends(
        "tax_id",
        "product_uom_qty",
        "product_id",
    )
    def _compute_ecotax_tax(self):
        return self._compute_ecotax()

    def _get_new_vals_list(self):
        if not self.subtotal_ecotax:
            return []
        return super()._get_new_vals_list()

    # ensure lines are re-generated in case ecotax_amount_unit of invoice line change
    # without changing the product
    @api.depends("ecotax_amount_unit", "subtotal_ecotax")
    def _compute_ecotax_line_ids(self):
        return super()._compute_ecotax_line_ids()

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

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        # remove ecoltax_line_ids value if empty in vals so it is recomputed during
        # invoice line creation. Example of use case : Ship a product not present in
        # SO. So line is created with qty 0 (so with no ecotax) but in invoice it is
        # added with a qty, with ecotax, so we want to recompute the ecotax report lines
        if "ecotax_line_ids" in res and not res["ecotax_line_ids"]:
            res.pop("ecotax_line_ids")
        return res
