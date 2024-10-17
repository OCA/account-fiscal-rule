# Copyright (C) 2015 -Today Aketion (http://www.akretion.com)
#   @author Renato Lima (https://twitter.com/renatonlima)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountProductFiscalClassificationTemplate(models.Model):
    _name = "account.product.fiscal.classification.template"
    _description = "Fiscal Classification Template"
    _order = "name"

    name = fields.Char(required=True, translate=True)

    description = fields.Text()

    chart_template_id = fields.Selection(
        string="Chart of Accounts",
        selection=lambda self: self.env[
            "account.chart.template"
        ]._select_chart_template(),
        required=True,
    )

    active = fields.Boolean(
        default=True,
        help="If unchecked, it will allow you to hide the Fiscal"
        " Classification Template without removing it.",
    )

    purchase_tax_ids = fields.Many2many(
        comodel_name="account.tax",
        relation="fiscal_classification_template_purchase_tax_rel",
        column1="fiscal_classification_id",
        column2="tax_id",
        string="Purchase Taxes",
        domain="[('type_tax_use', 'in', ['purchase', 'all'])]",
    )

    sale_tax_ids = fields.Many2many(
        comodel_name="account.tax",
        relation="fiscal_classification_template_sale_tax_rel",
        column1="fiscal_classification_id",
        column2="tax_id",
        string="Sale Taxes",
        domain="[('type_tax_use', 'in', ['sale', 'all'])]",
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
            purchase_tax_ids.append(taxes_ref[tax_template].id)
        for tax_template in self.sale_tax_ids:
            sale_tax_ids.append(taxes_ref[tax_template].id)

        return {
            "company_id": company.id,
            "name": self.name,
            "description": self.description,
            "purchase_tax_ids": [(6, 0, purchase_tax_ids)],
            "sale_tax_ids": [(6, 0, sale_tax_ids)],
        }
