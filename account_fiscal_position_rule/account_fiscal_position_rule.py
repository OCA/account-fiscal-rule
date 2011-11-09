# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2009  Renato Lima - Akretion                                    #
#                                                                               #
#This program is free software: you can redistribute it and/or modify           #
#it under the terms of the GNU Affero General Public License as published by    #
#the Free Software Foundation, either version 3 of the License, or              #
#(at your option) any later version.                                            #
#                                                                               #
#This program is distributed in the hope that it will be useful,                #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  #
#GNU General Public License for more details.                                   #
#                                                                               #
#You should have received a copy of the GNU General Public License              #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

from osv import fields, osv

class account_fiscal_position_rule(osv.osv):
    _name = "account.fiscal.position.rule"
    _columns = {
    	'name': fields.char('Name', size=64, required=True),
    	'description': fields.char('Description', size=128),
    	'from_country': fields.many2one('res.country','Country Form'),
    	'from_state': fields.many2one('res.country.state', 'State To', domain="[('country_id','=',from_country)]"),
    	'to_country': fields.many2one('res.country', 'Country To'),
    	'to_state': fields.many2one('res.country.state', 'State To', domain="[('country_id','=',to_country)]"),
        'company_id': fields.many2one('res.company', 'Company', required=True, select=True),
    	'fiscal_position_id': fields.many2one('account.fiscal.position', 'Fiscal Position', domain="[('company_id','=',company_id)]", required=True, select=True),
        'use_sale' : fields.boolean('Use in sales order'),
        'use_invoice' : fields.boolean('Use in Invoices'),
        'use_purchase' : fields.boolean('Use in Purchases'),
        'use_picking' : fields.boolean('Use in Picking'),
    }
    
    def fiscal_position_map(self, cr, uid, partner_id=False, partner_invoice_id=False, company_id=False, context=None):

        result = {'fiscal_position': False}
                     
        if not partner_id or not company_id:
             return result

        obj_partner = self.pool.get("res.partner").browse(cr, uid, partner_id)
        obj_company = self.pool.get("res.company").browse(cr, uid, company_id)

        if not obj_partner or not obj_company:
            return result
        
        #Case 1: Parnter Specific Fiscal Posigion
        if obj_partner.property_account_position:
            result['fiscal_position'] = obj_partner.property_account_position.id
            return result
        
        #Case 2: Rule based determination
        company_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_company.partner_id.id], ['invoice'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['invoice']])[0]
        
        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id

        if not partner_invoice_id:
            partner_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_partner.id], ['invoice'])
            partner_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [partner_addr['invoice']])[0]
        else:
            partner_addr_default = self.pool.get('res.partner.address').browse(cr, uid, partner_invoice_id)

        to_country = partner_addr_default.country_id.id
        to_state = partner_addr_default.state_id.id
        
        use_domain = context.get('use_domain', ('use_sale', '=', True))
        
        domain = ['&',('company_id','=', company_id), use_domain,
                  '|',('from_country','=',from_country),('from_country','=',False), 
                  '|',('to_country','=',to_country),('to_country','=',False), 
                  '|',('from_state','=',from_state),('from_state','=',False), 
                  '|',('to_state','=',to_state),('to_state','=',False),]  
        
        fsc_pos_id = self.search(cr, uid, domain)
        
        if fsc_pos_id:
            obj_fpo_rule = self.pool.get('account.fiscal.position.rule').browse(cr, uid, fsc_pos_id)[0]
            result['fiscal_position'] = obj_fpo_rule.fiscal_position_id.id
        
        return result
    
account_fiscal_position_rule()

class account_fiscal_position_rule_template(osv.osv):
    _name = "account.fiscal.position.rule.template"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.char('Description', size=128),
        'from_country': fields.many2one('res.country','Country Form'),
        'from_state': fields.many2one('res.country.state', 'State From', domain="[('country_id','=',from_country)]"),
        'to_country': fields.many2one('res.country', 'Country To'),
        'to_state': fields.many2one('res.country.state', 'State To', domain="[('country_id','=',to_country)]"),
        'fiscal_position_id': fields.many2one('account.fiscal.position.template', 'Fiscal Position', required=True),
        'use_sale' : fields.boolean('Use in sales order'),
        'use_invoice' : fields.boolean('Use in Invoices'),
        'use_purchase' : fields.boolean('Use in Purchases'),
        'use_picking' : fields.boolean('Use in Picking'),
    }
account_fiscal_position_rule_template()

class wizard_account_fiscal_position_rule(osv.osv_memory):
    _name='wizard.account.fiscal.position.rule'
    
    _columns = {
        'company_id':fields.many2one('res.company','Company',required=True),
    }
    
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr,uid,[uid],c)[0].company_id.id,
    }

    def action_create(self, cr, uid, ids, context=None):
        obj_wizard = self.browse(cr,uid,ids[0])
        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        obj_fiscal_position_rule_template = self.pool.get('account.fiscal.position.rule.template')

        company_id = obj_wizard.company_id.id
        
        pfr_ids = obj_fiscal_position_rule_template.search(cr, uid, [])
        
        for fpr_template in obj_fiscal_position_rule_template.browse(cr, uid, pfr_ids):
            vals = {
                    'name': fpr_template.name,
                    'description': fpr_template.description,
                    'from_country': fpr_template.from_country.id,
                    'from_state': fpr_template.from_state.id,
                    'to_country': fpr_template.to_country.id,
                    'to_state': fpr_template.to_state.id,
                    'company_id': company_id,
                    'fiscal_position_id': fpr_template.fiscal_position_id.id,
                    'fiscal_operaton_id': fpr_template.fiscal_operation_id.id,
                    'use_sale' : fpr_template.use_sale,
                    'use_invoice' : fpr_template.use_invoice,
                    'use_purchase' : fpr_template.use_purchase,
                    'use_picking' : fpr_template.use_picking,
                    }
            obj_fiscal_position_rule.create(cr,uid,vals)

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

wizard_account_fiscal_position_rule()