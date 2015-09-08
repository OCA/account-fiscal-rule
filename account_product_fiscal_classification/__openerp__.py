# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product - Taxes Group module for Odoo
#    Copyright (C) 2014-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Product - Taxes Group',
    'summary': 'Simplify taxes management for products with Taxes Group',
    'version': '1.0',
    'category': 'product',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir_model_access.yml',
        'view/view_related.xml',
        'view/action.xml',
        'view/view.xml',
        'view/menu.xml',
    ],
    'demo': [
        'demo/account_tax.yml',
        'demo/tax_group.yml',
        'demo/product_template.yml',
        'demo/res_groups.yml',
    ],
}
