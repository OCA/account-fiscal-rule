# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountProductFiscalClassification(models.Model):
    _name = "account.product.fiscal.classification"
    _description = "Fiscal Classification"

    # Default Section
    def _default_company_id(self):
        return self.env.company

    name = fields.Char(required=True, translate=True)

    description = fields.Text()

    active = fields.Boolean(
        default=True,
        help="If unchecked, it will allow you to hide the Fiscal"
        " Classification without removing it.",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=_default_company_id,
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

    usage_group_id = fields.Many2one(
        comodel_name="res.groups",
        string="Usage Group",
        help="If defined"
        ", the user should be member to this group, to use this fiscal"
        " classification when creating or updating products",
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
        res = super(AccountProductFiscalClassification, self).write(vals)
        pt_obj = self.env["product.template"]
        if "purchase_tax_ids" in vals or "sale_tax_ids" in vals:
            for fc in self:
                pt_lst = pt_obj.browse([x.id for x in fc.product_tmpl_ids])
                pt_lst.write({"fiscal_classification_id": fc.id})
        return res

    def unlink(self):
        for fc in self:
            if fc.product_tmpl_qty != 0:
                raise ValidationError(
                    _(
                        "You cannot delete The Fiscal Classification '%s' because"
                        " it contents %s products. Please move products"
                        " to another Fiscal Classification first."
                    )
                    % (fc.name, fc.product_tmpl_qty)
                )
        return super(AccountProductFiscalClassification, self).unlink()

    # Custom Sections
    @api.model
    def find_or_create(self, company_id, sale_tax_ids, purchase_tax_ids):
        at_obj = self.env["account.tax"]
        # Search for existing Fiscal Classification

        fcs = self.search(["|", ("active", "=", False), ("active", "=", True)])

        for fc in fcs:
            if (
                fc.company_id.id == company_id
                and sorted(fc.sale_tax_ids.ids) == sorted(sale_tax_ids)
                and sorted(fc.purchase_tax_ids.ids) == sorted(purchase_tax_ids)
            ):
                return fc.id

        # create new Fiscal classification if not found
        if not sale_tax_ids and not purchase_tax_ids:
            name = _("No taxes")
        elif not purchase_tax_ids:
            name = _("No Purchase Taxes - Sale Taxes: ")
            for tax in at_obj.browse(sale_tax_ids):
                name += tax.description and tax.description or tax.name
                name += " + "
            name = name[:-3]
        elif not sale_tax_ids:
            name = _("Purchase Taxes: ")
            for tax in at_obj.browse(purchase_tax_ids):
                name += tax.description and tax.description or tax.name
                name += " + "
            name = name[:-3]
            name += _("- No Sale Taxes")
        else:
            name = _("Purchase Taxes: ")
            for tax in at_obj.browse(purchase_tax_ids):
                name += tax.description and tax.description or tax.name
                name += " + "
            name = name[:-3]
            name += _(" - Sale Taxes: ")
            for tax in at_obj.browse(sale_tax_ids):
                name += tax.description and tax.description or tax.name
                name += " + "
            name = name[:-3]
        return self.create(
            {
                "name": name,
                "company_id": company_id,
                "sale_tax_ids": [(6, 0, sale_tax_ids)],
                "purchase_tax_ids": [(6, 0, purchase_tax_ids)],
            }
        ).id
