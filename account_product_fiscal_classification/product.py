# -*- en# -*- encoding: utf-8 -*-
################################################################################
#                                                                              #
# Copyright (C) 2010  Raphaël Valyi, Renato Lima - Akretion                    #
#                                                                              #
#This program is free software: you can redistribute it and/or modify          #
#it under the terms of the GNU Affero General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or             #
#(at your option) any later version.                                           #
#                                                                              #
#This program is distributed in the hope that it will be useful,               #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                 #
#GNU General Public License for more details.                                  #
#                                                                              #
#You should have received a copy of the GNU General Public License             #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.         #
################################################################################

from osv import fields, osv

class product_template(osv.osv):
    _inherit = 'product.template'
    
    _columns = {
                'property_fiscal_classification': fields.property(
                    'account.product.fiscal.classification',
                    type='many2one',
                    relation='account.product.fiscal.classification',
                    string="Fiscal Classification",
                    method=True,
                    view_load=True,
                    help="Company wise (eg localizable) Fiscal Classification"),
                }

    def fiscal_classification_id_change(self, cr, uid, ids, fiscal_classification_id=False, sale_tax_ids=[[6, 0, []]], purchase_tax_ids=[[6, 0, []]]):
        """We eventually keep the sale and purchase taxes because those are not company wise in OpenERP. So if we choose a different fiscal position
        for a different company, we don't want to override other's companies setting"""
        result = {'value':{}}
        if fiscal_classification_id:
            fiscal_classification = self.pool.get('account.product.fiscal.classification').browse(cr, uid, fiscal_classification_id)

            current_company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            to_keep_sale_tax_ids = self.pool.get('account.tax').search(cr, uid, [('id', 'in', sale_tax_ids[0][2]), ('company_id', '!=', current_company_id)])
            to_keep_purchase_tax_ids = self.pool.get('account.tax').search(cr, uid, [('id', 'in', purchase_tax_ids[0][2]), ('company_id', '!=', current_company_id)])

            result['value']['taxes_id'] = to_keep_sale_tax_ids + [x.id for x in fiscal_classification.sale_base_tax_ids]
            result['value']['supplier_taxes_id'] = to_keep_purchase_tax_ids + [x.id for x in fiscal_classification.purchase_base_tax_ids]
        return result

product_template()

class product_product(osv.osv):
    _inherit = "product.product"

    def fiscal_classification_id_change(self, cr, uid, ids, fiscal_classification_id=False, sale_tax_ids=[[6, 0, []]], purchase_tax_ids=[[6, 0, []]]):
        """We eventually keep the sale and purchase taxes because those are not company wise in OpenERP. So if we choose a different fiscal position
        for a different company, we don't want to override other's companies setting"""
        
        result = self.pool.get('product.template').fiscal_classification_id_change(cr, uid, ids, fiscal_classification_id, sale_tax_ids=[[6, 0, []]], purchase_tax_ids=[[6, 0, []]])
        return result
    
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: