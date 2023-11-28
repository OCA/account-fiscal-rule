#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountFiscalPositionTax (models.Model):
    _inherit = 'account.fiscal.position.tax'

    product_ids = fields.Many2many(
        comodel_name='product.product',
        string="Products",
    )
    product_category_ids = fields.Many2many(
        comodel_name='product.category',
        string="Product Categories",
    )

    @api.multi
    def is_product_tax_mapping(self):
        """
        True if any tax mapping in `self`
        has a product or a product category.
        """
        for tax_mapping in self:
            if tax_mapping.product_ids or tax_mapping.product_category_ids:
                is_product = True
                break
        else:
            is_product = False
        return is_product

    @api.multi
    def match_product(self, product):
        """
        Return the first mapping in `self` that matches `product`.

        A mapping matches `product`
        when `product` is declared in the mapping,
        or when its category is declared in the mapping.
        """
        for tax_line in self:
            if product in tax_line.product_ids \
               or product.categ_id in tax_line.product_category_ids:
                break
        else:
            tax_line = self.browse()
        return tax_line

    def map_taxes(self, taxes):
        """
        Map each tax in `taxes` using mappings in `self`.

        When a tax matches `tax_src_id`,
        then `tax_dest_id` is its mapped tax,
        otherwise the tax is mapped to itself.
        """
        result = self.env['account.tax'].browse()
        for tax in taxes:
            for tax_mapping in self:
                tax_src = tax_mapping.tax_src_id
                tax_dest = tax_mapping.tax_dest_id
                if tax_src == tax and tax_dest:
                    result |= tax_dest
                    break
            else:
                # No mapping matching `tax`: return original tax
                result |= tax
        return result
