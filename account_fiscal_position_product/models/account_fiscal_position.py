#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountFiscalPosition (models.Model):
    _inherit = 'account.fiscal.position'

    def is_product_fiscal_position(self):
        """
        True if any tax mapping in `self.tax_ids`
        has a product or a product category.
        """
        tax_mappings = self.mapped('tax_ids')
        return tax_mappings.is_product_tax_mapping()

    @api.model
    def map_tax(self, taxes, product=None, partner=None):
        """
        If this is a product fiscal position,
        only apply tax mappings matching `product`.
        Otherwise, return the usual mapping (defined in `super`).
        """
        if self.is_product_fiscal_position():
            if product is not None:
                matching_tax_mappings = self.tax_ids.filtered(
                    lambda tax_mapping: tax_mapping.match_product(product)
                )
                if matching_tax_mappings:
                    result = matching_tax_mappings.map_taxes(taxes)
                else:
                    # No mapping matching `product`: return original taxes
                    result = taxes
            else:
                # No `product`: return original taxes
                result = taxes
        else:
            result = super().map_tax(taxes, product=product, partner=partner)
        return result
