# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from lxml import builder

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    taxes_id = fields.Many2many(readonly=True, default=False)

    supplier_taxes_id = fields.Many2many(readonly=True, default=False)

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
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        self._alter_view_fiscal_classification(arch, view_type)
        return arch, view

    @api.model
    def _alter_view_fiscal_classification(self, arch, view_type):
        if view_type in ("form", "tree"):
            node_taxes_id = arch.xpath("//field[@name='taxes_id']")
            node_supplier_taxes_id = arch.xpath("//field[@name='supplier_taxes_id']")
            node_tax_field = node_taxes_id or node_supplier_taxes_id
            if node_tax_field:
                # append fiscal_classification_id just before taxes fields
                node_tax_field = node_tax_field[0]
                classification_node = builder.E.field(
                    name="fiscal_classification_id", required="1"
                )
                node_tax_field.getparent().insert(
                    node_tax_field.getparent().index(node_tax_field),
                    classification_node,
                )

            if view_type == "tree":
                if node_taxes_id:
                    node_taxes_id[0].set("optional", "hide")
                if node_supplier_taxes_id:
                    node_supplier_taxes_id[0].set("optional", "hide")

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
