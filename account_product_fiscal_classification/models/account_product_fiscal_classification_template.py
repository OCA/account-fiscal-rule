# -*- coding: utf-8 -*-
# Copyright (C) 2015 -Today Aketion (http://www.akretion.com)
#   @author Renato Lima (https://twitter.com/renatonlima)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountProductFiscalClassificationTemplate(models.Model):
    """Fiscal Classification model of customer and supplier taxes.
    This classification is used to create Fiscal Classification
    and Fiscal Classification template."""
    _name = 'account.product.fiscal.classification.template'
    _inherit = 'account.product.fiscal.classification.model'

    purchase_tax_ids = fields.Many2many(
        comodel_name='account.tax.template',
        relation='fiscal_classification_template_purchase_tax_rel',
        column1='fiscal_classification_id', column2='tax_id',
        string='Purchase Taxes', oldname="purchase_base_tax_ids",
        domain="[('type_tax_use', 'in', ['purchase', 'all'])]")

    sale_tax_ids = fields.Many2many(
        comodel_name='account.tax.template',
        relation='fiscal_classification_template_sale_tax_rel',
        column1='fiscal_classification_id', column2='tax_id',
        string='Sale Taxes', oldname="sale_base_tax_ids",
        domain="[('type_tax_use', 'in', ['sale', 'all'])]")
