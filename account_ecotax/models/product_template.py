# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ecotax_line_product_ids = fields.One2many(
        "ecotax.line.product",
        "product_tmpl_id",
        string="Ecotax lines",
        copy=True,
    )
    ecotax_amount = fields.Float(
        digits="Ecotax",
        compute="_compute_ecotax",
        help="Ecotax Amount computed from Classification",
        store=True,
    )
    fixed_ecotax = fields.Float(
        compute="_compute_ecotax",
        help="Fixed ecotax of the Ecotax Classification",
        store=True,
    )
    weight_based_ecotax = fields.Float(
        compute="_compute_ecotax",
        help="Ecotax value :\nproduct weight * ecotax coef of Ecotax Classification",
        store=True,
    )

    @api.depends(
        "ecotax_line_product_ids",
        "ecotax_line_product_ids.classification_id",
        "ecotax_line_product_ids.classification_id.ecotax_type",
        "ecotax_line_product_ids.classification_id.ecotax_coef",
        "ecotax_line_product_ids.force_amount",
        "weight",
    )
    def _compute_ecotax(self):
        for tmpl in self:
            amount_ecotax = 0.0
            weight_based_ecotax = 0.0
            fixed_ecotax = 0.0
            for ecotaxline_prod in tmpl.ecotax_line_product_ids:
                ecotax_cls = ecotaxline_prod.classification_id
                if ecotax_cls.ecotax_type == "weight_based":
                    weight_based_ecotax += ecotaxline_prod.amount
                else:
                    fixed_ecotax += ecotaxline_prod.amount
                amount_ecotax += ecotaxline_prod.amount
            tmpl.fixed_ecotax = fixed_ecotax
            tmpl.weight_based_ecotax = weight_based_ecotax
            tmpl.ecotax_amount = amount_ecotax
