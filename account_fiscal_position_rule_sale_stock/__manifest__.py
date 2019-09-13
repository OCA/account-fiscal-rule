# -*- coding: utf-8 -*-
# @ 2019 Akretion - www.akretion.com.br -
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Fiscal Position Rule Sale Stock',
    'version': '10.0.1.0.0',
    'category': 'Generic Modules/Accounting',
    'author': "Akretion,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'http://www.akretion.com',
    'depends': [
        'sale_stock',
        'account_fiscal_position_rule_stock',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
