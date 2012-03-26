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
#GNU Affero General Public License for more details.                            #
#                                                                               #
#You should have received a copy of the GNU Affero General Public License       #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

import time

from osv import fields, osv

class account_fiscal_position_rule(osv.osv):
    
    _name = "account.fiscal.position.rule"

    _order = 'sequence'

    _columns = {
            	'name': fields.char('Name', size=64, required=True),
            	'description': fields.char('Description', size=128),
            	'from_country': fields.many2one('res.country','Country From'),
            	'from_state': fields.many2one('res.country.state', 'State To', domain="[('country_id','=',from_country)]"),
            	'to_country': fields.many2one('res.country', 'Country To'),
            	'to_state': fields.many2one('res.country.state', 'State To', domain="[('country_id','=',to_country)]"),
                'company_id': fields.many2one('res.company', 'Company', required=True, select=True),
            	'fiscal_position_id': fields.many2one('account.fiscal.position', 'Fiscal Position', domain="[('company_id','=',company_id)]", required=True, select=True),
                'use_sale' : fields.boolean('Use in sales order'),
                'use_invoice' : fields.boolean('Use in Invoices'),
                'use_purchase' : fields.boolean('Use in Purchases'),
                'use_picking' : fields.boolean('Use in Picking'),
                'date_start': fields.date('Start Date', help="Starting date for this rule to be valid."),
                'date_end': fields.date('End Date', help="Ending date for this rule to be valid."),
                'sequence': fields.integer(
                    'Priority', required=True,
                    help='The lowest number will be applied.'),
                }

    _defaults = {
        'sequence': 10,
    }

    def _map_domain(self, cr, uid, partner, partner_address, company, context=None):
        company_addr = self.pool.get('res.partner').address_get(
            cr, uid, [company.partner_id.id], ['invoice'])
        company_addr_default = self.pool.get('res.partner.address').browse(
            cr, uid, [company_addr['invoice']])[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id

        to_country = partner_address.country_id.id
        to_state = partner_address.state_id.id

        document_date = context.get('date', time.strftime('%Y-%m-%d'))

        use_domain = context.get('use_domain', ('use_sale', '=', True))

        return ['&',('company_id','=', company.id), use_domain,
                '|',('from_country','=',from_country), ('from_country','=',False),
                '|',('to_country','=',to_country), ('to_country','=',False),
                '|',('from_state','=',from_state), ('from_state','=',False),
                '|',('to_state','=',to_state), ('to_state','=',False),
                '|',('date_start', '=', False), ('date_start', '<=', document_date),
                '|',('date_end', '=', False), ('date_end', '>=', document_date), ]

    def fiscal_position_map(self, cr, uid, partner_id=False, partner_invoice_id=False, company_id=False, context=None):

        result = {'fiscal_position': False}

        if not partner_id or not company_id:
             return result

        rule_pool = self.pool.get('account.fiscal.position.rule')
        obj_partner = self.pool.get("res.partner").browse(cr, uid, partner_id)
        obj_company = self.pool.get("res.company").browse(cr, uid, company_id)

        #Case 1: Partner Specific Fiscal Position
        if obj_partner.property_account_position:
            result['fiscal_position'] = obj_partner.property_account_position.id
            return result

        if not partner_invoice_id:
            partner_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_partner.id], ['invoice'])
            partner_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [partner_addr['invoice']])[0]
        else:
            partner_addr_default = self.pool.get('res.partner.address').browse(cr, uid, partner_invoice_id)

        #Case 2: Rule based determination
        domain = self._map_domain(
            cr, uid, obj_partner, partner_addr_default, obj_company, context=context)
        
        fsc_pos_id = self.search(cr, uid, domain,  context=context)

        if fsc_pos_id:
            obj_fpo_rule = rule_pool.browse(cr, uid, fsc_pos_id, context=context)[0]
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
                'date_start': fields.date('Start Date', help="Starting date for this rule to be valid."),
                'date_end': fields.date('End Date', help="Ending date for this rule to be valid."),
                'sequence': fields.integer(
                    'Priority', required=True,
                    help='The lowest number will be applied.'),
                }

    _defaults = {
        'sequence': 10,
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
        obj_fiscal_position_template = self.pool.get('account.fiscal.position.template')
        obj_fiscal_position = self.pool.get('account.fiscal.position')

        company_id = obj_wizard.company_id.id
        
        pfr_ids = obj_fiscal_position_rule_template.search(cr, uid, [])
        
        for fpr_template in obj_fiscal_position_rule_template.browse(cr, uid, pfr_ids):
            
            fp_id = False
            
            if fpr_template.fiscal_position_id:
                
                fp_id = obj_fiscal_position.search(cr, uid, [('name','=',fpr_template.fiscal_position_id.name)])
                
                if not fp_id:
                    continue
            
            vals = {
                    'name': fpr_template.name,
                    'description': fpr_template.description,
                    'from_country': fpr_template.from_country.id,
                    'from_state': fpr_template.from_state.id,
                    'to_country': fpr_template.to_country.id,
                    'to_state': fpr_template.to_state.id,
                    'company_id': company_id,
                    'fiscal_position_id': fp_id[0],
                    'use_sale' : fpr_template.use_sale,
                    'use_invoice' : fpr_template.use_invoice,
                    'use_purchase' : fpr_template.use_purchase,
                    'use_picking' : fpr_template.use_picking,
                    'date_start': fpr_template.date_start,
                    'date_end': fpr_template.date_end,
                    'sequence': fpr_template.sequence,
                    }

            obj_fiscal_position_rule.create(cr,uid,vals)

        return {}

wizard_account_fiscal_position_rule()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
