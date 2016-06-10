# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import UserError
from avalara_api import AvaTaxService, BaseAddress #, Line

class AccountTax(models.Model):
    """Inherit to implement the tax using avatax API"""
    _inherit = "account.tax"
    
    is_avatax = fields.Boolean('Is Avatax')


    @api.model
    def _get_compute_tax(self, avatax_config, doc_date, doc_code, doc_type, partner, ship_from_address, shipping_address,
                          lines, user=None, exemption_number=None, exemption_code_name=None, commit=False, invoice_date=False, reference_code=False, location_code=False, context=None):
        currency_code = self.env.user.company_id.currency_id.name

        if not partner.customer_code:
            if not avatax_config.auto_generate_customer_code:
                raise UserError(_('Customer Code for customer %s not defined.\n\n  You can edit the Customer Code in customer profile. You can fix by clicking "Generate Customer Code" button in the customer contact information"'% (partner.name)))
            else:
                partner.generate_cust_code() 
                        
                        
        if not shipping_address:
            raise UserError(_('There is no shipping address defined for the partner.'))        
        #it's show destination address
#        shipping_address = address_obj.browse(cr, uid, shipping_address_id, context=context)
#        if not lines:
#            raise osv.except_osv(_('AvaTax: Error !'), _('AvaTax needs at least one sale order line defined for tax calculation.'))
        
        if not ship_from_address:
            raise UserError(_('There is no company address defined.'))

        #it's show source address
#        ship_from_address = address_obj.browse(cr, uid, ship_from_address_id, context=context)
        
        #this condition is required, in case user select force address validation on AvaTax API Configuration
        if not avatax_config.address_validation:
            if avatax_config.force_address_validation:
                if not shipping_address.date_validation:
                    raise UserError(_('Please validate the shipping address for the partner %s.'
                                % (partner.name)))

#        if not avatax_config.address_validation:
            if not ship_from_address.date_validation:
                raise UserError(_('Please validate the company address.'))

        #For check credential
        avalara_obj = AvaTaxService(avatax_config.account_number, avatax_config.license_key,
                                 avatax_config.service_url, avatax_config.request_timeout, avatax_config.logging)
        avalara_obj.create_tax_service()
        addSvc = avalara_obj.create_address_service().addressSvc
        origin = BaseAddress(addSvc, ship_from_address.street or None,
                             ship_from_address.street2 or None,
                             ship_from_address.city, ship_from_address.zip,
                             ship_from_address.state_id and ship_from_address.state_id.code or None,
                             ship_from_address.country_id and ship_from_address.country_id.code or None, 0).data
        destination = BaseAddress(addSvc, shipping_address.street or None,
                                  shipping_address.street2 or None,
                                  shipping_address.city, shipping_address.zip,
                                  shipping_address.state_id and shipping_address.state_id.code or None,
                                  shipping_address.country_id and shipping_address.country_id.code or None, 1).data
        
        #using get_tax method to calculate tax based on address   
#        doc_date = datetime.strftime(datetime.strptime(doc_date,DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
#        print"doc_date",type(doc_date)
        invoice_date = invoice_date.split(' ')[0] if invoice_date else False
        result = avalara_obj.get_tax(avatax_config.company_code, doc_date, doc_type,
                                 partner.customer_code, doc_code, origin, destination,
                                 lines, exemption_number,
                                 exemption_code_name,
                                 user and user.name or None, commit, invoice_date, reference_code, location_code, currency_code, partner.vat_id or None)
        
        return result

    @api.model
    def cancel_tax(self, avatax_config, doc_code, doc_type, cancel_code):
         """Sometimes we have not need to tax calculation, then method is used to cancel taxation"""
         avalara_obj = AvaTaxService(avatax_config.account_number, avatax_config.license_key,
                                  avatax_config.service_url, avatax_config.request_timeout,
                                  avatax_config.logging)
         avalara_obj.create_tax_service()
         try:
             result = avalara_obj.get_tax_history(avatax_config.company_code, doc_code, doc_type)
         except:
             return True
        
         result = avalara_obj.cancel_tax(avatax_config.company_code, doc_code, doc_type, cancel_code)
         return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
