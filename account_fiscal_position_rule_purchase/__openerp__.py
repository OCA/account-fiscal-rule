# -*- coding: utf-8 -*-
#   Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
#   Copyright 2012 Camptocamp SA
#     @author: Guewen Baconnier
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Account Fiscal Position Rule Purchase',
    'version': '9.0.1.0.0',
    'category': 'Generic Modules/Accounting',
    'author': "Akretion,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'http://www.akretion.com',
    'depends': [
        'account_fiscal_position_rule',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [
        'test/account_fiscal_position_rule_purchase.yml',
    ],
    'installable': False,
}
