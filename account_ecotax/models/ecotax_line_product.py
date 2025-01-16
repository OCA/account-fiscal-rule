# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EcotaxLineProduct(models.Model):
    """class for objects which can be used to save mutiple ecotax classifications
    by product."""

    _name = "ecotax.line.product"
    _description = "Ecotax Line product"

    product_tmpl_id = fields.Many2one(
        "product.template", string="Product Template", readonly=True
    )
    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    currency_id = fields.Many2one(related="product_tmpl_id.currency_id", readonly=True)
    classification_id = fields.Many2one(
        "account.ecotax.classification",
        string="Classification",
    )
    force_amount = fields.Float(
        digits="Ecotax",
        help="Force ecotax amount.\n"
        "Allow to substitute default Ecotax Classification",
    )
    amount = fields.Float(
        digits="Ecotax",
        compute="_compute_ecotax",
        help="Ecotax Amount computed form Classification or forced ecotax amount",
        store=True,
    )
    display_name = fields.Char(compute="_compute_display_name")

    @api.depends("classification_id", "amount")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s (%s)" % (
                rec.classification_id.name,
                rec.amount,
            )

    @api.depends(
        "classification_id",
        "classification_id.ecotax_type",
        "classification_id.ecotax_coef",
        "product_tmpl_id",
        "product_tmpl_id.weight",
        "product_id",
        "product_id.weight",
        "force_amount",
    )
    def _compute_ecotax(self):
        for ecotaxline in self:
            ecotax_cls = ecotaxline.classification_id

            if ecotax_cls.ecotax_type == "weight_based":
                amount = ecotax_cls.ecotax_coef * (
                    ecotaxline.product_tmpl_id.weight
                    or ecotaxline.product_id.weight
                    or 0.0
                )
            else:
                amount = ecotax_cls.default_fixed_ecotax
            # force ecotax amount
            if ecotaxline.force_amount:
                amount = ecotaxline.force_amount
            ecotaxline.amount = amount

    _sql_constraints = [
        (
            "unique_classification_id_by_product",
            "UNIQUE(classification_id, product_id)",
            "Only one ecotax classification occurrence by product",
        ),
        (
            "unique_classification_id_by_product_tmpl",
            "UNIQUE(classification_id, product_tmpl_id)",
            "Only one ecotax classification occurrence by product Template",
        ),
    ]
