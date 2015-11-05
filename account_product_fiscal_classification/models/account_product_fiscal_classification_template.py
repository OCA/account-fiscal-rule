# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Product - Fiscal Classification module for Odoo
#    Copyright (C) 2015 -Today Aketion (http://www.akretion.com)
#    @author Renato Lima (https://twitter.com/renatonlima)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import models, fields


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
        string='Purchase Taxes', oldname="purchase_base_tax_ids", domain="""[
            ('parent_id', '=', False),
            ('type_tax_use', 'in', ['purchase', 'all'])]""")

    sale_tax_ids = fields.Many2many(
        comodel_name='account.tax.template',
        relation='fiscal_classification_template_sale_tax_rel',
        column1='fiscal_classification_id', column2='tax_id',
        string='Sale Taxes', oldname="sale_base_tax_ids", domain="""[
            ('parent_id', '=', False),
            ('type_tax_use', 'in', ['sale', 'all'])]""")
