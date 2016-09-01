# -*- coding: utf-8 -*-
# Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Renato Lima <renato.lima@akretion.com>
# Copyright 2012-TODAY Camptocamp SA
#   @author: Guewen Baconnier
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Account Fiscal Position Rule',
    'version': '8.0.1.2.0',
    'category': 'Generic Modules/Accounting',
    'description': """Include a rule to decide the correct fiscal position""",
    'author': "Akretion,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'http://www.akretion.com',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_fiscal_position_rule_view.xml',
        'security/account_fiscal_position_rule_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': ['test/test_rules.yml'],
    'installable': True,
}
