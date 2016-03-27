# -*- coding: utf-8 -*-
# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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
