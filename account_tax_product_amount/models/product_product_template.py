# Copyright 2025 Pierre Verkest <pierre@verkest.fr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model_create_multi
    def create(self, vals_list):
        """Store the initial standard price in order to be able
        to retrieve the cost of a product template for a given date"""
        templates = super().create(vals_list)
        templates._maintain_product_variant_tax_amount_consistency()
        return templates

    def write(self, vals):
        res = super().write(vals)
        if "taxes_id" in vals or "supplier_taxes_id" in vals:
            self._maintain_product_variant_tax_amount_consistency()
        return res

    def _maintain_product_variant_tax_amount_consistency(self):
        for product_template in self:
            expected_fixed_product_amount_taxes = (
                product_template.taxes_id.sudo().filtered(
                    lambda tax: tax.amount_type == "fixed" and tax.use_product_amount
                )
                | product_template.supplier_taxes_id.sudo().filtered(
                    lambda tax: tax.amount_type == "fixed" and tax.use_product_amount
                )
            )
            for variant in product_template.with_context(
                active_test=False
            ).product_variant_ids:
                to_add = (
                    expected_fixed_product_amount_taxes
                    - variant.tax_amount_ids.sudo().tax_id
                )
                to_remove = (
                    variant.tax_amount_ids.sudo().tax_id
                    - expected_fixed_product_amount_taxes
                )
                variant.tax_amount_ids.sudo().filtered(
                    lambda tax_amount, to_remove=to_remove: tax_amount.tax_id
                    in to_remove
                ).unlink()
                variant.tax_amount_ids += variant.tax_amount_ids.sudo().create(
                    [
                        {
                            "product_id": variant.id,
                            "tax_id": tax.id,
                            "company_id": tax.company_id.id,
                            "amount": tax.amount,
                        }
                        for tax in to_add
                    ]
                )
