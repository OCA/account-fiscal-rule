# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule_sale_shop for OpenERP
#   Copyright (C) 2013-2014 credativ ltd. <http://www.credativ.co.uk>
#     @author Kinner Vachhani <kinner.vachhani@credativ.co.uk>
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

from osv import fields, orm


class account_fiscal_position_rule(orm.Model):
    _inherit = 'account.fiscal.position.rule'

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop'),
        }

    def _map_domain(self, cr, uid, partner, addrs, company,
                    context=None, **kwargs):
        domain = super(account_fiscal_position_rule, self)._map_domain(
            cr, uid, partner, addrs, company, context=context, **kwargs)
        if kwargs.get('shop_id', False):
            domain += [
                '|',
                ('shop_id', '=', kwargs.get('shop_id')),
                ('shop_id', '=', False),
                ]
        return domain
