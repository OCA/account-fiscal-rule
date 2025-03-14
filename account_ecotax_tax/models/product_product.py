# Copyright 2021 Camptocamp
#   @author Silvio Gregorini <silvio.gregorini@camptocamp.com>
# Copyright 2023 Akretion (http://www.akretion.com)
# #   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    ecotax_amount_context = fields.Float(
        digits="Ecotax",
        compute="_compute_product_ecotax_context",
        help="Ecotax Amount computed form all ecotax line classification, but depending"
        " of the context (delivery country)",
    )

    @api.depends(
        "all_ecotax_line_product_ids",
        "all_ecotax_line_product_ids.classification_id",
        "all_ecotax_line_product_ids.classification_id.ecotax_type",
        "all_ecotax_line_product_ids.classification_id.ecotax_coef",
        "all_ecotax_line_product_ids.force_amount",
        "weight",
    )
    @api.depends_context("country")
    def _compute_product_ecotax_context(self):
        for product in self:
            country = self.env.context.get("country", False)
            eligible_classifications = product._get_country_eligible_classification(
                country
            )
            (
                _fixed_ecotax,
                _weight_based_ecotax,
                amount_ecotax,
            ) = product._get_ecotax_amounts_from_classification(
                eligible_classifications
            )
            product.ecotax_amount_context = amount_ecotax
