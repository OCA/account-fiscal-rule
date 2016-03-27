# -*- coding: utf-8 -*-
# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Product - Fiscal Classification',
    'summary': 'Simplify taxes management for products',
    'version': '8.0.3.0.0',
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
        'views/view_product_template.xml',
        'views/action.xml',
        'views/view_product_category.xml',
        'views/view_account_product_fiscal_classification.xml',
        'views/view_wizard_change_fiscal_classification.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/account_tax.xml',
        'demo/account_product_fiscal_classification.xml',
        'demo/product_template.xml',
        'demo/product_category.xml',
        'demo/res_company.xml',
        'demo/res_groups.xml',
        'demo/res_users.xml',
    ],
    'images': [
        'static/description/img/fiscal_classification_form.png',
        'static/description/img/product_template_accounting_setting.png'
    ],
    'post_init_hook':
        'create_fiscal_classification_from_product_template',
}
