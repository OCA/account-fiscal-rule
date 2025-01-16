# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class EcotaxLineMixin(models.AbstractModel):
    """Mixin class for objects which can be used to save
     multi ecotax classification  by account move line
    or sale order line."""

    _name = "ecotax.line.mixin"
    _description = "Ecotax Line Mixin"

    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    currency_id = fields.Many2one("res.currency", string="Currency")
    classification_id = fields.Many2one(
        "account.ecotax.classification",
        string="Classification",
    )
    amount_unit = fields.Float(
        digits="Ecotax",
        compute="_compute_ecotax",
        help="Ecotax Amount computed from Classification or Manual ecotax",
        store=True,
    )
    force_amount_unit = fields.Float(
        digits="Ecotax",
        help="Force ecotax.\n"
        "Allow to add a subtitle to the default Ecotax Classification",
    )
    amount_total = fields.Float(
        digits="Ecotax",
        compute="_compute_ecotax",
        help="Ecotax Amount total computed from Classification or forced ecotax amount",
        store=True,
    )
    quantity = fields.Float(digits="Product Unit of Measure", readonly=True)

    @api.depends(
        "classification_id",
        "force_amount_unit",
        "product_id",
        "quantity",
    )
    def _compute_ecotax(self):
        for ecotaxline in self:
            ecotax_classif = ecotaxline.classification_id

            if ecotaxline.force_amount_unit:
                # force ecotax amount
                amount = ecotaxline.force_amount_unit
            elif ecotax_classif.ecotax_type == "weight_based":
                amount = ecotax_classif.ecotax_coef * (
                    ecotaxline.product_id.weight or 0.0
                )
            else:
                amount = ecotax_classif.default_fixed_ecotax

            ecotaxline.amount_unit = amount
            total = ecotaxline.amount_unit * ecotaxline.quantity
            if ecotaxline.currency_id:
                total = ecotaxline.currency_id.round(total)
            ecotaxline.amount_total = total
