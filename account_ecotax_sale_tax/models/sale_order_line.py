# © 2015 -2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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
    def _compute_ecotax(self):
        return super()._compute_ecotax()

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
