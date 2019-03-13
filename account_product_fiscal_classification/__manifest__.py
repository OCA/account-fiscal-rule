# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Product - Fiscal Classification',
    'summary': 'Simplify taxes management for products',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'Akretion,GRAP,La Louve,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-fiscal-rule',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/view_related.xml',
        'views/action.xml',
        'views/view.xml',
        'views/menu.xml',
        'views/view_product_category.xml',
    ],
    'installable': True,
}
