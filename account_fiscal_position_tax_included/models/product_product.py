# Copyright (C) 2019 - Today: Sylvain LE GAL (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Full Copy Paste of the original function, defined in the odoo account module.
    # One single line is changed
    @api.model
    def _get_tax_included_unit_price_from_price(
        self,
        product_price_unit,
        currency,
        product_taxes,
        fiscal_position=None,
        product_taxes_after_fp=None,
        is_refund_document=False,
    ):
        if not product_taxes:
            return product_price_unit

        if product_taxes_after_fp is None:
            if not fiscal_position:
                return product_price_unit

            product_taxes_after_fp = fiscal_position.map_tax(product_taxes)

        flattened_taxes_after_fp = (
            product_taxes_after_fp._origin.flatten_taxes_hierarchy()
        )
        flattened_taxes_before_fp = product_taxes._origin.flatten_taxes_hierarchy()

        # <Begin of Changes>
        # taxes_before_included = all(tax.price_include for tax in flattened_taxes_before_fp)
        taxes_before_included = True
        # </End of Changes>

        if (
            set(product_taxes.ids) != set(product_taxes_after_fp.ids)
            and taxes_before_included
        ):
            taxes_res = flattened_taxes_before_fp.with_context(
                round=False, round_base=False
            ).compute_all(
                product_price_unit,
                quantity=1.0,
                currency=currency,
                product=self,
                is_refund=is_refund_document,
            )
            product_price_unit = taxes_res["total_excluded"]

            if any(tax.price_include for tax in flattened_taxes_after_fp):
                taxes_res = flattened_taxes_after_fp.with_context(
                    round=False, round_base=False
                ).compute_all(
                    product_price_unit,
                    quantity=1.0,
                    currency=currency,
                    product=self,
                    is_refund=is_refund_document,
                    handle_price_include=False,
                )
                for tax_res in taxes_res["taxes"]:
                    tax = self.env["account.tax"].browse(tax_res["id"])
                    if tax.price_include:
                        product_price_unit += tax_res["amount"]

        return product_price_unit
