# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule_stock for OpenERP
#   Copyright (C) 2009 Akretion <http://www.akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Account Fiscal Position Rule Stock',
    'version': '1.1',
    'category': 'Generic Modules/Accounting',
    'author': "Akretion,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'http://www.akretion.com',
    'depends': [
        'account_fiscal_position_rule',
        'stock',
    ],
    'data': [
        'views/stock_picking.xml',
        'security/account_fiscal_position_rule_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
}
