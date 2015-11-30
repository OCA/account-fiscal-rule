# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Product - Fiscal Classification module for Odoo
#    Copyright (C) 2014-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

{
    'name': 'Account Product - Fiscal Classification',
    'summary': 'Simplify taxes management for products',
    'version': '8.0.2.1.0',
    'category': 'Accounting',
    'author': 'Akretion,GRAP,Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir_model_access.yml',
        'views/view_related.xml',
        'views/action.xml',
        'views/view.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/account_tax.yml',
        'demo/account_tax_template.yml',
        'demo/account_product_fiscal_classification.yml',
        'demo/account_product_fiscal_classification_template.yml',
        'demo/product_template.yml',
        'demo/res_company.yml',
        'demo/res_groups.yml',
        'demo/res_users.yml',
    ],
    'images': [
        'static/description/img/fiscal_classification_form.png',
        'static/description/img/product_template_accounting_setting.png'
    ],
    'post_init_hook':
        'create_fiscal_classification_from_product_template',
}
