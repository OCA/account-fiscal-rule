# -*- encoding: utf-8 -*-
#########################################################################
#                                                                       #
# Copyright (C) 2009  Rapha�l Valyi                                     #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

from osv import fields, osv

class account_product_fiscal_classification(osv.osv):
    _name = 'account.product.fiscal.classification'
    _description = 'Product Fiscal Classification'
    _columns = {
        'name': fields.char('Main code', size=32, required=True),
        'description': fields.char('Description', size=64),
        'sale_base_tax_ids': fields.many2many('account.tax', 'fiscal_classification_sale_tax_rel', 'fiscal_classification_id', 'tax_id', 'Base Sale Taxes', domain=[('type_tax_use','!=','purchase')]),
        'purchase_base_tax_ids': fields.many2many('account.tax', 'fiscal_classification_purchase_tax_rel', 'fiscal_classification_id', 'tax_id', 'Base Sale Taxes', domain=[('type_tax_use','!=','sale')]),
    }

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            ids = self.search(cr, user, [('name', '=', name)] + args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('description', '=', name)] + args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
                ids += self.search(cr, user, [('description', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

account_product_fiscal_classification()


class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {'fiscal_classification_id': fields.many2one('account.product.fiscal.classification', 'Fiscal Classification'),}

    def fiscal_classification_id_change(self, cr, uid, ids, fiscal_classification_id=False):
        result = {'value':{}}
        if fiscal_classification_id:
            fiscal_classification = self.pool.get('account.product.fiscal.classification').browse(cr, uid, fiscal_classification_id)
            
            result['value']['taxes_id'] = [x.id for x in fiscal_classification.sale_base_tax_ids]
            result['value']['supplier_taxes_id'] = [x.id for x in fiscal_classification.purchase_base_tax_ids]
        return result
            

product_product()