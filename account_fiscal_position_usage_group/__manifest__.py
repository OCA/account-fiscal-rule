# Copyright (C) 2019-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Fiscal Position - Usage Group',
    'summary': 'Limit the usage of fiscal positions to defined groups members',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'maintainers': ['legalsylvain'],
    'development_status': 'Beta',
    'website': 'https://github.com/OCA/account-fiscal-rule',
    'license': 'AGPL-3',
    'depends': [
        'account_coa_menu',
    ],
    'data': [
        'views/view_account_fiscal_position.xml',
        'views/view_account_fiscal_position_template.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/account_fiscal_position.xml',
    ],
    'installable': True,
}
