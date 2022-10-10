# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fiscal_classification_id = fields.Many2one(
        comodel_name="account.product.fiscal.classification",
        string="Fiscal Classification",
        tracking=True,
        help="Specify the combination of taxes for this product."
        " This field is required. If you dont find the correct Fiscal"
        " Classification, Please create a new one or ask to your account"
        " manager if you don't have the access right.",
    )

    # Overload Section
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._update_vals_fiscal_classification(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._update_vals_fiscal_classification(vals)
        res = super().write(vals)
        return res

    # View Section
    @api.onchange("fiscal_classification_id")
    def _onchange_fiscal_classification_id(self):
        self.supplier_taxes_id = self.fiscal_classification_id.purchase_tax_ids.ids
        self.taxes_id = self.fiscal_classification_id.sale_tax_ids.ids

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        doc = etree.fromstring(result["arch"])
        nodes = doc.xpath("//field[@name='fiscal_classification_id']")
        if nodes:
            for node in nodes:
                modifiers = json.loads(node.get("modifiers", "{}"))
                modifiers["required"] = True
                node.set("modifiers", json.dumps(modifiers))
            result["arch"] = etree.tostring(doc, encoding="unicode").replace("\t", "")
        return result

    # Custom Section
    def _update_vals_fiscal_classification(self, vals):
        FiscalClassification = self.env["account.product.fiscal.classification"]
        if vals.get("fiscal_classification_id", False):
            # We use sudo to have access to all the taxes, even taxes that belong
            # to companies that the user can't access in the current context
            classification = FiscalClassification.sudo().browse(
                vals.get("fiscal_classification_id")
            )
            vals.update(
                {
                    "supplier_taxes_id": [(6, 0, classification.purchase_tax_ids.ids)],
                    "taxes_id": [(6, 0, classification.sale_tax_ids.ids)],
                }
            )
        elif vals.get("supplier_taxes_id") or vals.get("taxes_id"):
            raise ValidationError(
                _(
                    "You can not create or write products with"
                    " 'Customer Taxes' or 'Supplier Taxes'\n."
                    "Please, use instead the 'Fiscal Classification' field."
                )
            )
        return vals

    @api.constrains("categ_id", "fiscal_classification_id")
    def _check_rules_fiscal_classification(self):
        self.env["account.product.fiscal.rule"].check_product_templates_integrity(self)
