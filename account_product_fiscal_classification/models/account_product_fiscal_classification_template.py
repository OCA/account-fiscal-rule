# Copyright (C) 2015 -Today Aketion (http://www.akretion.com)
#   @author Renato Lima (https://twitter.com/renatonlima)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountProductFiscalClassificationTemplate(models.Model):
    _name = "account.product.fiscal.classification.template"
    _description = "Fiscal Classification Template"

    name = fields.Char(required=True, translate=True)

    description = fields.Text()

    chart_template_id = fields.Many2one(
        comodel_name="account.chart.template",
        string="Chart Template",
        required=True,
    )

    active = fields.Boolean(
        default=True,
        help="If unchecked, it will allow you to hide the Fiscal"
        " Classification Template without removing it.",
    )

    purchase_tax_ids = fields.Many2many(
        comodel_name="account.tax.template",
        relation="fiscal_classification_template_purchase_tax_rel",
        column1="fiscal_classification_id",
        column2="tax_id",
        string="Purchase Taxes",
        domain="["
        "('type_tax_use', 'in', ['purchase', 'all']),"
        "('chart_template_id', '=', chart_template_id),"
        "]",
    )

    sale_tax_ids = fields.Many2many(
        comodel_name="account.tax.template",
        relation="fiscal_classification_template_sale_tax_rel",
        column1="fiscal_classification_id",
        column2="tax_id",
        string="Sale Taxes",
        domain="["
        "('type_tax_use', 'in', ['sale', 'all']),"
        "('chart_template_id', '=', chart_template_id),"
        "]",
    )

    usage_group_id = fields.Many2one(
        comodel_name="res.groups",
        string="Usage Group",
        help="If defined"
        ", the user should be member to this group, to use this fiscal"
        " classification when creating or updating products",
    )

    def _prepare_fiscal_classification(self, company, taxes_ref):
        """Prepare fiscal classification values
        :param company: company the wizard is running for
        :param taxes_ref: Mapping between ids of tax templates and
          real taxes created from them
        """
        self.ensure_one()
        purchase_tax_ids = []
        sale_tax_ids = []
        for tax_template in self.purchase_tax_ids:
            purchase_tax_ids.append(taxes_ref[tax_template.id])
        for tax_template in self.sale_tax_ids:
            sale_tax_ids.append(taxes_ref[tax_template.id])

        return {
            "company_id": company.id,
            "name": self.name,
            "usage_group_id": self.usage_group_id.id,
            "description": self.description,
            "purchase_tax_ids": [(6, 0, purchase_tax_ids)],
            "sale_tax_ids": [(6, 0, sale_tax_ids)],
        }
