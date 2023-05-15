# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountProductFiscalClassification(models.Model):
    _name = "account.product.fiscal.classification"
    _description = "Fiscal Classification"

    name = fields.Char(required=True)

    description = fields.Text()

    active = fields.Boolean(
        default=True,
        help="If unchecked, it will allow you to hide the Fiscal"
        " Classification without removing it.",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        help="Specify a company"
        " if you want to define this Fiscal Classification only for specific"
        " company. Otherwise, this Fiscal Classification will be available"
        " for all companies.",
    )

    product_tmpl_ids = fields.One2many(
        comodel_name="product.template",
        string="Products",
        compute="_compute_product_tmpl_info",
    )

    product_tmpl_qty = fields.Integer(
        string="Products Quantity", compute="_compute_product_tmpl_info"
    )

    purchase_tax_ids = fields.Many2many(
        comodel_name="account.tax",
        relation="fiscal_classification_purchase_tax_rel",
        column1="fiscal_classification_id",
        column2="tax_id",
        string="Purchase Taxes",
        domain="""[
            ('type_tax_use', 'in', ['purchase', 'all'])]""",
    )

    sale_tax_ids = fields.Many2many(
        comodel_name="account.tax",
        relation="fiscal_classification_sale_tax_rel",
        column1="fiscal_classification_id",
        column2="tax_id",
        string="Sale Taxes",
        domain="""[
            ('type_tax_use', 'in', ['sale', 'all'])]""",
    )

    # Compute Section
    def _compute_product_tmpl_info(self):
        for record in self:
            res = (
                record.env["product.template"]
                .with_context(active_test=False)
                .search([("fiscal_classification_id", "=", record.id)])
            )
            record.product_tmpl_ids = res
            record.product_tmpl_qty = len(res)

    # Overload Section
    def write(self, vals):
        res = super().write(vals)
        ProductTemplate = (
            self.env["product.template"].sudo().with_context(active_test=False)
        )
        if "purchase_tax_ids" in vals or "sale_tax_ids" in vals:
            for classification in self:
                templates = ProductTemplate.search(
                    [("fiscal_classification_id", "=", classification.id)]
                )
                templates.write({"fiscal_classification_id": classification.id})
        return res

    def unlink(self):
        ProductTemplate = (
            self.env["product.template"].sudo().with_context(active_test=False)
        )
        for classification in self:
            templates = ProductTemplate.search(
                [("fiscal_classification_id", "=", classification.id)]
            )
            if len(templates) != 0:
                raise ValidationError(
                    _(
                        "You cannot delete The Fiscal Classification"
                        " '%(classification_name)s' because"
                        " it contents %(qty)s products."
                        " Please move products"
                        " to another Fiscal Classification first.",
                        classification_name=classification.name,
                        qty=len(templates),
                    )
                )
        return super().unlink()

    # Custom Sections
    @api.model
    def _prepare_vals_from_taxes(self, purchase_taxes, sale_taxes):
        # Guess name
        if not sale_taxes and not purchase_taxes:
            name = _("No taxes")
        else:
            if not purchase_taxes:
                purchase_part = _("No Purchase Taxes")
            else:
                if len(purchase_taxes) == 1:
                    purchase_part = _("Purchase Tax: ")
                else:
                    purchase_part = _("Purchase Taxes: ")
                purchase_part += " + ".join(
                    [
                        tax.description and tax.description or tax.name
                        for tax in purchase_taxes
                    ]
                )
            if not sale_taxes:
                sale_part = _("No Sale Taxes")
            else:
                if len(sale_taxes) == 1:
                    sale_part = _("Sale Tax: ")
                else:
                    sale_part = _("Sale Taxes: ")
                sale_part += " + ".join(
                    [
                        tax.description and tax.description or tax.name
                        for tax in sale_taxes
                    ]
                )

            name = f"{purchase_part} - {sale_part}"

        # Set a company if all the taxes belong to the same company
        companies = (sale_taxes | purchase_taxes).mapped("company_id")
        company_id = len(companies) == 1 and companies[0].id or False
        vals = {
            "name": name,
            "sale_tax_ids": [(6, 0, sale_taxes.ids)],
            "purchase_tax_ids": [(6, 0, purchase_taxes.ids)],
            "company_id": company_id,
        }
        return vals
