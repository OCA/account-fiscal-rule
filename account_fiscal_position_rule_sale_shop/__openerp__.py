# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule_sale_shop for OpenERP
#   Copyright (C) 2013-2014 credativ ltd. <http://www.credativ.co.uk>
#     @author Ondrej Kuznik <ondrej.kuznik@credativ.co.uk>
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
    'name': 'Account Fiscal Position Rule Sale Shop',
    'version': '1.0.0',
    'category': 'Generic Modules/Accounting',
    'description': """Include a rule to decide the
    correct fiscal position for Sale per shop""",
    'author': 'credativ ltd.',
    'license': 'AGPL-3',
    'website': 'http://www.credativ.co.uk',
    'depends': [
        'account_fiscal_position_rule_sale',
    ],
    'data': [
        'account_fiscal_position_rule_view.xml',
    ],
    'demo': [],
    'installable': True,
}
