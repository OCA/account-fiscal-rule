#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Account Fiscal Position - Product',
    'summary': 'Apply fiscal position only for configured products',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'TAKOBI, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-fiscal-rule'
               '/tree/12.0/account_fiscal_position_product',
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_fiscal_position_views.xml',
    ],
}
