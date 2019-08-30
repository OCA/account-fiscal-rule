# -*- coding: utf-8 -*-
# @ 2009 Akretion - www.akretion.com.br -
# @author Renato Lima <renato.lima@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Fiscal Position Rule Stock',
    'version': '10.0.1.0.0',
    'category': 'Generic Modules/Accounting',
    'author': "Akretion, Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'http://www.akretion.com',
    'depends': [
        'account_fiscal_position_rule',
        'stock_picking_invoicing',
    ],
    'data': [
        'views/stock_picking.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/account_fiscal_position_rule_stock_demo.xml',
    ],
    'installable': True,
}
