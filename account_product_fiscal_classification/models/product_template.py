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

    # Overload Section
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._update_vals_fiscal_classification(vals, create_mode=True)
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
    def _update_vals_fiscal_classification(self, vals, create_mode=False):
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
        elif create_mode or {"supplier_taxes_id", "taxes_id"} & vals.keys():
            self._find_or_create_classification(vals)
        return vals

    @api.constrains("categ_id", "fiscal_classification_id")
    def _check_rules_fiscal_classification(self):
        self.env["account.product.fiscal.rule"].check_product_templates_integrity(self)

    def _find_or_create_classification(self, vals):
        """Find the correct Fiscal classification,
        depending of the taxes, or create a new one, if no one are found."""
        # search for matching classication
        purchase_tax_ids = vals.get("supplier_taxes_id", [])
        sale_tax_ids = vals.get("taxes_id", [])
        for elm in ("supplier_taxes_id", "taxes_id"):
            if elm in vals:
                del vals[elm]
        domain = [
            ("sale_tax_ids", "in", sale_tax_ids),
            ("purchase_tax_ids", "in", purchase_tax_ids),
        ]
        classification = self.env["account.product.fiscal.classification"].search(
            domain, limit=1
        )
        if not classification:
            # Create a dedicate classification for these taxes combination
            classif_vals = self.env[
                "account.product.fiscal.classification"
            ]._prepare_vals_from_taxes(
                self.env["account.tax"].browse(purchase_tax_ids),
                self.env["account.tax"].browse(sale_tax_ids),
            )
            classification = self.env["account.product.fiscal.classification"].create(
                classif_vals
            )
            _logger.info(
                f"Creating new Fiscal Classification '{classif_vals['name']}'"
                f" for {self.display_name}"
            )
        vals["fiscal_classification_id"] = classification.id
