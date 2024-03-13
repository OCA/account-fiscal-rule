#  Copyright 2022 Simone Rubino - TAKOBI
#  Copyright 2024 Damien Carlier - TOODIGIT
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountFiscalPositionTax(models.Model):
    _inherit = "account.fiscal.position.tax"

    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products",
    )
    product_category_ids = fields.Many2many(
        comodel_name="product.category",
        string="Product Categories",
    )

    @api.constrains("position_id", "tax_src_id", "product_ids", "product_category_ids")
    def _check_product_category(self):
        for mapping in self:
            domain = [
                ("id", "!=", mapping.id),
                ("position_id", "=", mapping.position_id.id),
                ("tax_src_id", "=", mapping.tax_src_id.id),
            ]
            mappings = self.search(domain)
            if mappings.product_ids & mapping.product_ids:
                raise UserError(
                    _(
                        "You cannot have many mappings for the same "
                        "source tax and the same product(s)."
                    )
                )
            if mappings.product_category_ids & mapping.product_category_ids:
                raise UserError(
                    _(
                        "You cannot have many mappings for the same "
                        "source tax and the same category(ies)."
                    )
                )
            if mapping.product_category_ids:
                new_categs = mapping.product_category_ids.mapped("parent_path")
                other_categs = mappings.product_category_ids.mapped("parent_path")
                for n_categ in new_categs:
                    for o_categ in other_categs:
                        if n_categ.startswith(o_categ) or o_categ.startswith(n_categ):
                            raise UserError(
                                _(
                                    "You cannot have many mappings for "
                                    "parent and child categories."
                                )
                            )
