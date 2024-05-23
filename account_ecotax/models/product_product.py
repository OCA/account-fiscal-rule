# Copyright 2021 Camptocamp
#   @author Silvio Gregorini <silvio.gregorini@camptocamp.com>
# Copyright 2023 Akretion (http://www.akretion.com)
# #   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    additional_ecotax_line_product_ids = fields.One2many(
        "ecotax.line.product",
        "product_id",
        string="Additional ecotax lines",
        copy=True,
        domain="[('id', 'not in', ecotax_line_product_ids)]",
    )
    all_ecotax_line_product_ids = fields.One2many(
        "ecotax.line.product",
        compute="_compute_all_ecotax_line_product_ids",
        search="_search_all_ecotax_line_product_ids",
        string="All ecotax lines",
        help="Contain all ecotaxs classification defined in product template"
        "and the additionnal.\n"
        "ecotaxs defined in product variant. For more details"
        "see the product variant accounting tab",
    )
    ecotax_amount = fields.Float(
        digits="Ecotax",
        compute="_compute_product_ecotax",
        help="Ecotax Amount computed form all ecotax line classification",
        store=True,
    )
    fixed_ecotax = fields.Float(
        compute="_compute_product_ecotax",
        help="Fixed ecotax of the Ecotax Classification",
    )
    weight_based_ecotax = fields.Float(
        compute="_compute_product_ecotax",
        help="Ecotax value :\n"
        "product weight * ecotax coef of "
        "Ecotax Classification",
    )

    @api.depends("ecotax_line_product_ids", "additional_ecotax_line_product_ids")
    def _compute_all_ecotax_line_product_ids(self):
        for product in self:
            product.all_ecotax_line_product_ids = (
                product.ecotax_line_product_ids
                | product.additional_ecotax_line_product_ids
            )

    def _search_all_ecotax_line_product_ids(self, operator, operand):
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            return [
                ("ecotax_line_product_ids", operator, operand),
                ("additional_ecotax_line_product_ids", operator, operand),
            ]
        return [
            "|",
            ("ecotax_line_product_ids", operator, operand),
            ("additional_ecotax_line_product_ids", operator, operand),
        ]

    @api.depends(
        "all_ecotax_line_product_ids",
        "all_ecotax_line_product_ids.classification_id",
        "all_ecotax_line_product_ids.classification_id.ecotax_type",
        "all_ecotax_line_product_ids.classification_id.ecotax_coef",
        "all_ecotax_line_product_ids.force_amount",
        "weight",
    )
    def _compute_product_ecotax(self):
        for product in self:
            amount_ecotax = 0.0
            weight_based_ecotax = 0.0
            fixed_ecotax = 0.0
            for ecotaxline_prod in product.all_ecotax_line_product_ids:
                ecotax_cls = ecotaxline_prod.classification_id
                if ecotax_cls.ecotax_type == "weight_based":
                    weight_based_ecotax += ecotaxline_prod.amount
                else:
                    fixed_ecotax += ecotaxline_prod.amount

                amount_ecotax += ecotaxline_prod.amount
            product.fixed_ecotax = fixed_ecotax
            product.weight_based_ecotax = weight_based_ecotax
            product.ecotax_amount = amount_ecotax
