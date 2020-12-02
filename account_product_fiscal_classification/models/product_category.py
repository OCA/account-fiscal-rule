# Copyright (C) 2016-Today La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = "product.category"

    # Field Section
    fiscal_restriction = fields.Boolean(
        string="Restriction on Fiscal Classifications",
        default=False,
        help="Check this box if you want to enable Restriction on Fiscal"
        " Classifications.",
    )

    fiscal_classification_ids = fields.Many2many(
        comodel_name="account.product.fiscal.classification",
        relation="product_category_fiscal_classification_rel",
        column1="product_category_id",
        column2="fiscal_classification_id",
        string="Allowed Fiscal Classifications",
        help="Specify Fiscal Classifications that will be allowed for products"
        " that belong to this Product Category.",
    )

    forbidden_classification_template_qty = fields.Integer(
        string="Quantity of Products with Forbidden Classification",
        compute="_compute_forbidden_classification",
    )

    forbidden_classification_template_ids = fields.Many2many(
        comodel_name="product.template",
        string="Products with Forbidden Classification",
        compute="_compute_forbidden_classification",
    )

    # Constraint Section
    @api.constrains("fiscal_restriction", "fiscal_classification_ids")
    def _check_fiscal_restriction(self):
        for categ in self:
            if (
                not categ.fiscal_restriction
                and len(categ.fiscal_classification_ids) > 0
            ):
                raise ValidationError(
                    _(
                        "You can not set fiscal classifications"
                        " on %s if Restriction on Fiscal Classifications is not"
                        " enabled for the category."
                    )
                    % (categ.name)
                )

    # Compute Section
    def _compute_forbidden_classification(self):
        template_obj = self.env["product.template"]
        for categ in self:
            if not categ.fiscal_restriction:
                template_ids = []
            else:
                template_ids = template_obj.search(
                    [
                        ("categ_id", "=", categ.id),
                        (
                            "fiscal_classification_id",
                            "not in",
                            categ.fiscal_classification_ids.ids,
                        ),
                    ]
                )
            categ.forbidden_classification_template_ids = template_ids
            categ.forbidden_classification_template_qty = len(template_ids)

    # Action Section
    def apply_classification_to_childs(self):
        for categ in self:
            childs = self.search([("parent_id", "=", categ.id)])
            # Apply Settings on direct childs
            childs.write(
                {
                    "fiscal_restriction": categ.fiscal_restriction,
                    "fiscal_classification_ids": [
                        [6, 0, categ.fiscal_classification_ids.ids]
                    ],
                }
            )
            # Recurring to apply settings to indirect childs
            childs.apply_classification_to_childs()
