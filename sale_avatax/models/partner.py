# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
import time
from random import random
from avalara_api import AvaTaxService, BaseAddress
from openerp.exceptions import UserError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class res_partner(models.Model):
    """Update partner information by adding new fields according to avalara partner configuration"""
    _inherit = 'res.partner'
    
    exemption_number = fields.Char('Exemption Number', help="Indicates if the customer is exempt or not")
    exemption_code_id = fields.Many2one('exemption.code', 'Exemption Code', help="Indicates the type of exemption the customer may have")
#    tax_schedule_id = fields.Many2one('tax.schedule', 'Tax Schedule', help="Identifies customers using AVATAX. Only customers with AVATAX designation triggers tax calculation from AvaTax otherwise it will follow the normal tax calculation that OpenERP provides")
    date_validation = fields.Date('Last Validation Date', readonly=True, help="The date the address was last validated by AvaTax and accepted")
    validation_method = fields.Selection([('avatax', 'AVALARA'), ('usps', 'USPS'), ('other', 'Other')], 'Address Validation Method', readonly=True, help="It gets populated when the address is validated by the method")
    latitude = fields.Char('Latitude')
    longitude = fields.Char('Longitude')
    validated_on_save = fields.Boolean('Validated On Save', help="Indicates if the address is already validated on save before calling the wizard")
    customer_code = fields.Char('Customer Code', required=False)
    tax_apply = fields.Boolean('Tax Calculation',help="Indicates the avatax calculation is compulsory")
    tax_exempt = fields.Boolean('Is Tax Exempt',help="Indicates the exemption tax calculation is compulsory")
    vat_id = fields.Char("VAT ID", help="Customers VAT number (Buyer VAT). Identifies the customer as a “Registered Business” and the tax engine will utilize that information in the tax decision process.")
    
    _sql_constraints = [
        ('name_uniq', 'unique(customer_code)', 'Customer Code must be unique!'),
    ]
    
    
    @api.multi
    def generate_cust_code(self):
        #Auto populate customer code
        customer_code = str(int(time.time()))+'-'+str(int(random()*10))+'-'+'Cust-'+str(self.id)                
        self.write({'customer_code': customer_code})
        
        
    def check_avatax_support(self, avatax_config, country_id):
        """ Checks if address validation pre-condition meets. """
        if avatax_config.address_validation:
            raise UserError(_("The AvaTax Address Validation Service is disabled by the administrator. Please make sure it's enabled for the address validation"))
        if country_id and country_id not in [x.id for x in avatax_config.country_ids] or not country_id:
#            return False
            raise UserError(_("The AvaTax Address Validation Service does not support this country in the configuration, please continue with your normal process."))
        return True
    
    @api.onchange('tax_exempt')
    def onchange_tax_exemption(self):
        if not self.tax_exempt:
            self.exemption_number = ''
            self.exemption_code_id = None
            

    def get_state_id(self, code, c_code):
        """ Returns the id of the state from the code. """
        state_obj = self.env['res.country.state']
        c_id = self.env['res.country'].search([('code', '=', c_code)])[0]
        s_id = state_obj.search([('code', '=', code),('country_id', '=',c_id.id)])
        if s_id: return s_id[0].id
        return False

    def get_country_id(self, code):
        """ Returns the id of the country from the code. """

        country_obj = self.env['res.country']
        country = country_obj.search([('code', '=', code)])
        if country: return country[0].id
        return False

    def get_state_code(self, state_id):
        """ Returns the code from the id of the state. """

        state_obj = self.env['res.country.state']
        return state_id and state_obj.browse(state_id).code

    def get_country_code(self, country_id):
        """ Returns the code from the id of the country. """

        country_obj = self.env['res.country']
        return country_id and country_obj.browse(country_id).code
    
    @api.multi
    def multi_address_validation(self):
        context = dict(self._context or {})
        add_val_ids = context.get('active_ids')
        partner_obj = self.env['res.partner']
        for val_id in add_val_ids:
            partner_brw = partner_obj.browse(val_id)
            vals = partner_brw.read(['street', 'street2', 'city', 'state_id', 'zip', 'country_id'])[0]
            vals['state_id'] = vals.get('state_id') and vals['state_id'][0]
            vals['country_id'] = vals.get('country_id') and vals['country_id'][0]
            
            avatax_config_obj = avatax_config_obj= self.env['avalara.salestax']
            avatax_config = avatax_config_obj._get_avatax_config_company()

            if avatax_config:
                try:
                    valid_address = self._validate_address(cr, uid, vals, avatax_config, context=context)
                    vals.update({
                        'street': valid_address.Line1,
                        'street2': valid_address.Line2,
                        'city': valid_address.City,
                        'state_id': self.get_state_id(valid_address.Region, valid_address.Country),
                        'zip': valid_address.PostalCode,
                        'country_id': self.get_country_id(valid_address.Country),
                        'latitude': valid_address.Latitude,
                        'longitude': valid_address.Longitude,
                        'date_validation': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'validation_method': 'avatax',
                        'validated_on_save': True
                    })
                    partner_brw.write(vals)
                except:
                    pass
#        mod_obj = self.pool.get('ir.model.data')
#        res = mod_obj.get_object_reference(cr, uid, 'base', 'view_partner_tree')
#        res_id = res and res[1] or False,

        return {
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'res.partner',
            'type':'ir.actions.act_window',
            'context': {'search_default_customer':1},
        }
        
    @api.multi
    def varify_address_validatation(self):
        """Method is used to verify of state and country """
        view_ref = self.env.ref('avatax_connector.view_avalara_salestax_address_validate', False)
        address = self.read(['street', 'street2', 'city', 'state_id', 'zip', 'country_id'])[0]
        address['state_id'] = address.get('state_id') and address['state_id'][0]
        address['country_id'] = address.get('country_id') and address['country_id'][0]
        
        # Get the valid result from the AvaTax Address Validation Service
        self._validate_address(address)
        ctx = self._context.copy()
        ctx.update({
            'active_ids': self.ids,
            'active_id': self.id
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Address Validation',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_ref.id,
            'res_model': 'avalara.salestax.address.validate',
            'nodestroy': True,
            'res_id': False , # assuming the many2one is (mis)named 'teacher'
            'target':'new',
            'context': ctx
        }
    

    def _validate_address(self, address, avatax_config=False):
        """ Returns the valid address from the AvaTax Address Validation Service. """
        avatax_config_obj= self.env['avalara.salestax']

        if not avatax_config:
            avatax_config = avatax_config_obj._get_avatax_config_company()

        if not avatax_config:            
            raise UserError(_("This module has not yet been setup.  Please refer to the Avatax module documentation."))

        # Create the AvaTax Address service with the configuration parameters set for the instance
        if (not avatax_config.account_number or not avatax_config.license_key or not avatax_config.service_url or not avatax_config.request_timeout):
            raise UserError(_("This module has not yet been setup.  Please refer to the Avatax module documentation."))
        
        avapoint = AvaTaxService(avatax_config.account_number, avatax_config.license_key,
                        avatax_config.service_url, avatax_config.request_timeout, avatax_config.logging)
        addSvc = avapoint.create_address_service().addressSvc

        # Obtain the state code & country code and create a BaseAddress Object
        state_code = address.get('state_id') and self.get_state_code(address['state_id'])
        country_code = address.get('country_id') and self.get_country_code(address['country_id'])
        baseaddress = BaseAddress(addSvc, address.get('street') or None, address.get('street2') or None,
                         address.get('city'), address.get('zip'), state_code, country_code, 0).data
        result = avapoint.validate_address(baseaddress, avatax_config.result_in_uppercase and 'Upper' or 'Default')
        
        valid_address = result.ValidAddresses[0][0]
        return valid_address

    def update_addresses(self, vals, from_write=False):
        """ Updates the vals dictionary with the valid address as returned from the Avalara Address Validation. """
        address = vals        
        if vals:
            if (vals.get('street') or vals.get('street2') or vals.get('zip') or vals.get('city') or \
                vals.get('country_id') or vals.get('state_id')):
                avatax_config_obj= self.env['avalara.salestax']
                avatax_config = avatax_config_obj._get_avatax_config_company()
    
                if avatax_config and avatax_config.validation_on_save:
                    brw_address = self.read(['street', 'street2', 'city', 'state_id', 'zip', 'country_id'])[0]
                    address['country_id'] = 'country_id' in vals and vals['country_id'] or brw_address.get('country_id') and brw_address['country_id'][0]
                    if self.check_avatax_support(avatax_config, address['country_id']):
                        if from_write:
                            address['street'] = 'street' in vals and vals['street'] or brw_address.get('street') or ''
                            address['street2'] = 'street2' in vals and vals['street2'] or brw_address.get('street2') or ''
                            address['city'] = 'city' in vals and vals['city'] or brw_address.get('city') or ''
                            address['zip'] = 'zip' in vals and vals['zip'] or brw_address.get('zip') or ''
                            address['state_id'] = 'state_id' in vals and vals['state_id'] or brw_address.get('state_id') and brw_address['state_id'][0] or False
                            
                        valid_address = self._validate_address(address, avatax_config)
                        vals.update({
                            'street': valid_address.Line1,
                            'street2': valid_address.Line2,
                            'city': valid_address.City,
                            'state_id': self.get_state_id(valid_address.Region, valid_address.Country),
                            'zip': valid_address.PostalCode,
                            'country_id': self.get_country_id(valid_address.Country),
                            'latitude': valid_address.Latitude,
                            'longitude': valid_address.Longitude,
                            'date_validation': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                            'validation_method': 'avatax',
                            'validated_on_save': True
                        })
        return vals

    @api.model
    def create(self, vals):
        if vals.get('parent_id') and vals.get('use_parent_address'):
            domain_siblings = [('parent_id', '=', vals['parent_id']), ('use_parent_address', '=', True)]
            update_ids = [vals['parent_id']] + self.search(domain_siblings)
            vals = self.update_addresses(update_ids, vals)
        else:
            address = vals
            if (vals.get('street') or vals.get('street2') or vals.get('zip') or vals.get('city') or \
                vals.get('country_id') or vals.get('state_id')):
                avatax_config_obj= self.env['avalara.salestax']
                avatax_config = avatax_config_obj._get_avatax_config_company()
                if vals.get('tax_exempt'):
                    if not vals.get('exemption_number') and not vals.get('exemption_code_id'):
                        raise UserError(_("Please enter either Exemption Number or Exemption Code for marking customer as Exempt."))
                
                
                #It will work when user want to validate address at customer creation, check option in avalara api form
                if avatax_config and avatax_config.validation_on_save:
                    
                    if self.check_avatax_support(avatax_config, address.get('country_id')):
#                        fields_to_read = filter(lambda x: x not in vals, ['street', 'street2', 'city', 'state_id', 'zip', 'country_id'])
#                        print"self.read(fields_to_read)",self.read(fields_to_read)
#                        address = fields_to_read and self.read(fields_to_read)[0] or {}
#                        print"address",address
#                        address['state_id'] = address.get('state_id') and address['state_id'][0]
#                        address['country_id'] = address.get('country_id') and address['country_id'][0]
#                        address.update(vals)
    
                        valid_address = self._validate_address(address, avatax_config)
                        vals.update({
                            'street': valid_address.Line1,
                            'street2': valid_address.Line2,
                            'city': valid_address.City,
                            'state_id': self.get_state_id(valid_address.Region, valid_address.Country),
                            'zip': valid_address.PostalCode,
                            'country_id': self.get_country_id(valid_address.Country),
                            'latitude': valid_address.Latitude,
                            'longitude': valid_address.Longitude,
                            'date_validation': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                            'validation_method': 'avatax',
                            'validated_on_save': True
                        })
         
        # execute the create                
        cust_id = super(res_partner, self).create(vals)

        # Generate a detailed customer code based on timestamp, a random number, and it's  ID                
        customer_code = str(int(time.time()))+'-'+str(int(random()*10))+'-'+'Cust-'+str(cust_id.id)
               
        #Auto populate customer code
        cust_id.write({'customer_code': customer_code})
        return cust_id

    @api.multi
    def write(self, vals):
        if not vals:
            vals.update({
                'latitude': '',
                'longitude': '',
                'date_validation': False,
                'validation_method': '',
                'validated_on_save': False,
            })

        #when tax exempt check then atleast exemption number or exemption code should be filled            
        if vals.get('tax_exempt', False):
            if not vals.get('exemption_number', False) and not vals.get('exemption_code_id', False):
                raise UserError(_('Please enter either Exemption Number or Exemption Code for marking customer as Exempt.'))
        # Follow the normal write process if it's a write operation from the wizard
        if self.env.context.get('from_validate_button', False):
            return super(res_partner, self).write(vals)
        vals1 = self.update_addresses(vals, True)
        return super(res_partner, self).write(vals1)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: