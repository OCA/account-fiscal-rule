# coding: utf-8
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Fiscal Position - Type',
    'summary': 'Add sale / purchase type on fiscal position',
    'version': '8.0.1.0.0',
    'category': 'Accounting',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'depends': [
        'account',
    ],
    'data': [
        'views/view_account_fiscal_position.xml',
        'views/view_account_fiscal_position_template.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
    ],
    'images': [
        'static/description/fiscal_position_form.png',
    ],
}
