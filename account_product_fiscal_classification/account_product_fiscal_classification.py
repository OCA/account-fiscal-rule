# -*- encoding: utf-8 -*-
#########################################################################
#                                                                       #
# Copyright (C) 2010  Raphaël Valyi                                     #
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
        'company_id': fields.many2one('res.company', 'Company'),
         #TODO restrict to company_id if company_id set when framework will allow it:
        'sale_base_tax_ids': fields.many2many('account.tax', 'fiscal_classification_sale_tax_rel', 'fiscal_classification_id', 'tax_id', 'Base Sale Taxes', domain=[('type_tax_use','!=','purchase')]),
        'purchase_base_tax_ids': fields.many2many('account.tax', 'fiscal_classification_purchase_tax_rel', 'fiscal_classification_id', 'tax_id', 'Base Purchase Taxes', domain=[('type_tax_use','!=','sale')]),
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

class account_product_fiscal_classification_template(osv.osv):
    _name = 'account.product.fiscal.classification.template'
    _description = 'Product Fiscal Classification Template'
    _columns = {
        'name': fields.char('Main code', size=32, required=True),
        'description': fields.char('Description', size=64),
         #TODO restrict to company_id if company_id set when framework will allow it:
        'sale_base_tax_ids': fields.many2many('account.tax.template', 'fiscal_classification_template_sale_tax_rel', 'fiscal_classification_id', 'tax_id', 'Base Sale Taxes', domain=[('type_tax_use','!=','purchase')]),
        'purchase_base_tax_ids': fields.many2many('account.tax.template', 'fiscal_classification_template_purchase_tax_rel', 'fiscal_classification_id', 'tax_id', 'Base Purchase Taxes', domain=[('type_tax_use','!=','sale')]),
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

account_product_fiscal_classification_template()

class wizard_account_product_fiscal_classification(osv.osv_memory):
    
    _name='wizard.account.product.fiscal.classification'

    _columns = {
        'company_id':fields.many2one('res.company','Company',required=True),
    }
    
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr,uid,[uid],c)[0].company_id.id,
    }

    def action_create(self, cr, uid, ids, context=None):
        obj_wizard = self.browse(cr,uid,ids[0])
        obj_tax = self.pool.get('account.tax')
        obj_tax_template = self.pool.get('account.tax.template')
        obj_fiscal_classification = self.pool.get('account.product.fiscal.classification')
        obj_fiscal_classification_template = self.pool.get('account.product.fiscal.classification.template')

        company_id = obj_wizard.company_id.id
        tax_template_ref = {}
        
        tax_ids = obj_tax.search(cr,uid,[('company_id','=',company_id)])
        
        for tax in obj_tax.browse(cr,uid,tax_ids):
            tax_template = obj_tax_template.search(cr,uid,[('name','=',tax.name)])[0]
            
            if tax_template:
                tax_template_ref[tax_template] = tax.id
        
        fclass_ids_template = obj_fiscal_classification_template.search(cr, uid, [])
        
        for fclass_template in obj_fiscal_classification_template.browse(cr, uid, fclass_ids_template):
            
            fclass_id = obj_fiscal_classification.search(cr, uid, [('name','=',fclass_template.name)])
            
            if not fclass_id: 
                sale_tax_ids = []
                for tax in fclass_template.sale_base_tax_ids:
                    sale_tax_ids.append(tax_template_ref[tax.id])
                
                purchase_tax_ids = []
                for tax in fclass_template.purchase_base_tax_ids:
                    purchase_tax_ids.append(tax_template_ref[tax.id])
                
                vals = {
                        'name': fclass_template.name,
                        'description': fclass_template.description,
                        'company_id': company_id,
                        'sale_base_tax_ids': [(6,0,sale_tax_ids)],
                        'purchase_base_tax_ids': [(6,0,purchase_tax_ids)]
                        }
                obj_fiscal_classification.create(cr,uid,vals)
            
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
        }
    def action_cancel(self,cr,uid,ids,conect=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
        }
        
wizard_account_product_fiscal_classification()
