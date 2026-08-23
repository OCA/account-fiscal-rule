# Copyright 2025 Pierre Verkest <pierre@verkest.fr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    use_product_amount = fields.Boolean(
        default=False,
        help=(
            "If checked, the tax amount is taken from the "
            "product variant (with a fallback to the tax amount)."
        ),
    )

    def _eval_tax_amount_fixed_amount(self, batch, raw_base, evaluation_context):
        """Override to use the product variant tax amount
        if the tax is set to use product amount."""
        product_tax_amount = (
            evaluation_context.get("product").get("fixed_tax_amounts", {}).get(self.id)
        )
        if (
            self.amount_type == "fixed"
            and self.use_product_amount
            and product_tax_amount
        ):
            sign = -1 if evaluation_context["price_unit"] < 0.0 else 1
            return sign * evaluation_context["quantity"] * product_tax_amount

        return super()._eval_tax_amount_fixed_amount(
            batch, raw_base, evaluation_context
        )

    @api.model
    def _eval_taxes_computation_prepare_product_values(
        self, default_product_values, product=None
    ):
        product_values = super()._eval_taxes_computation_prepare_product_values(
            default_product_values, product
        )
        if product and product._name == "product.product":
            product_values["fixed_tax_amounts"] = {}
            for tax_amount in product.tax_amount_ids:
                if tax_amount.tax_id.use_product_amount:
                    product_values["fixed_tax_amounts"][tax_amount.tax_id.id] = (
                        tax_amount.amount
                    )
        return product_values
