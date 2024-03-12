# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_product_fiscal_classification for OpenERP
#   Copyright (C) 2010-TODAY Akretion <http://www.akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
#     @author Raphaël Valyi <rvalyi@akretion.com>
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
    'name': 'Account Product Fiscal Classification',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'Akretion',
    'description': """Account Product Fiscal Classification""",
    'website': 'http://www.akretion.com',
    'depends': [
        'account',
        'product',
    ],
    'data': [
        'product_view.xml',
        'account_product_fiscal_classification_data.xml',
        'account_product_fiscal_classification_view.xml',
        'security/account_product_fiscal_classification_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'active': False,
}
