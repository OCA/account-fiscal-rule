# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging

from lxml import etree

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    taxes_id = fields.Many2many(default=False)

    supplier_taxes_id = fields.Many2many(default=False)

    fiscal_classification_id = fields.Many2one(
        comodel_name="account.product.fiscal.classification",
        string="Fiscal Classification",
        tracking=True,
        help="Specify the combination of taxes for this product."
        " This field is required. If you dont find the correct Fiscal"
        " Classification, Please create a new one or ask to your account"
        " manager if you don't have the access right.",
    )

    @api.constrains("categ_id", "fiscal_classification_id")
    def _check_rules_fiscal_classification(self):
        self.env["account.product.fiscal.rule"].check_product_templates_integrity(self)

    # Overload Section
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._fiscal_classification_update_taxes(vals)
        templates = super().create(vals_list)
        for template in templates.filtered(lambda x: not x.fiscal_classification_id):
            template.fiscal_classification_id = (
                template._fiscal_classification_get_or_create()[0]
            )
        return templates

    def write(self, vals):
        self._fiscal_classification_update_taxes(vals)
        res = super().write(vals)
        if ({"supplier_taxes_id", "taxes_id"} & vals.keys()) and (
            "fiscal_classification_id" not in vals.keys()
        ):
            for template in self:
                new_classification = template._fiscal_classification_get_or_create()[0]
                if template.fiscal_classification_id != new_classification:
                    template.fiscal_classification_id = new_classification
        return res

    # View Section
    @api.onchange("fiscal_classification_id")
    def _onchange_fiscal_classification_id(self):
        self.supplier_taxes_id = self.fiscal_classification_id.purchase_tax_ids.ids
        self.taxes_id = self.fiscal_classification_id.sale_tax_ids.ids

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Set fiscal_classification_id required on all views.
        We don't set the field required by field definition to avoid
        incompatibility with other modules, errors on import, etc..."""
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
    def _fiscal_classification_update_taxes(self, vals):
        """if fiscal classification is in vals, update vals to set
        according purchase and sale taxes"""
        FiscalClassification = self.env["account.product.fiscal.classification"]
        if vals.get("fiscal_classification_id"):
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
        return vals

    def _fiscal_classification_get_or_create(self):
        """get the classification(s) that matches with the fiscal settings
        of the current product.
        If no configuration is found, create a new one.
        This will raise an error, if current user doesn't have the access right
        to create one classification."""

        self.ensure_one()

        FiscalClassification = self.env["account.product.fiscal.classification"]
        FiscalClassificationSudo = found_classifications = self.env[
            "account.product.fiscal.classification"
        ].sudo()
        all_classifications = FiscalClassificationSudo.search(
            [("company_id", "in", [self.company_id.id, False])]
        )

        for classification in all_classifications:
            if sorted(self.supplier_taxes_id.ids) == sorted(
                classification.purchase_tax_ids.ids
            ) and sorted(self.taxes_id.ids) == sorted(classification.sale_tax_ids.ids):
                found_classifications |= classification

        if len(found_classifications) == 0:
            vals = FiscalClassification._prepare_vals_from_taxes(
                self.supplier_taxes_id, self.taxes_id
            )
            _logger.info(f"Creating new Fiscal Classification '{vals['name']}' ...")
            return FiscalClassification.create(vals)

        return found_classifications
