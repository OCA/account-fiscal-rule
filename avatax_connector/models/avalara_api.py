# -*- coding: utf-8 -*-

import suds
import socket
import urllib2
import string
import os
import datetime
#import base64
from openerp import tools
from openerp.tools.translate import _
from openerp import fields
from openerp.exceptions import UserError

class AvaTaxService:

    def enable_log(self):
        import logging, tempfile
        logger = logging.getLogger('suds.client')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(os.path.join(tempfile.gettempdir(), "soap-messages.log"))
        logger.propagate = False
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def __init__(self, username, password, url, timeout, enable_log=False):
        self.username = username    #This is the company's Development/Production Account number
        self.password = password #Put in the License Key received from AvaTax
        self.url = url
        self.timeout = timeout
        enable_log and self.enable_log()
        
    def create_tax_service(self):
        self.taxSvc = self.service('tax')
        return self

    def create_address_service(self):
        self.addressSvc = self.service('address')
        return self
    
    def create_account_service(self):
        self.accountSvc = self.service('account')
        return self
    

    def service(self, name):
        nameCap = string.capitalize(name) # So this will be 'Tax' or 'Address'
        # The Python SUDS library can fetch the WSDL down from the server
        # or use a local file URL. We'll use a local file URL.
#        wsdl_url = 'file:///' + os.getcwd().replace('\\', '/') + '/%ssvc.wsdl.xml' % name
        # If you want to fetch the WSDL from the server, use this instead:
        wsdl_url = 'https://avatax.avalara.net/%s/%ssvc.wsdl' % (nameCap, nameCap)
        
        try:
             svc = suds.client.Client(url=wsdl_url)
        except urllib2.URLError, details:
            raise UserError(_(details))
        else:
            svc.set_options(service='%sSvc' % nameCap)
            svc.set_options(port='%sSvcSoap' % nameCap)
            svc.set_options(location='%s/%s/%sSvc.asmx' % (self.url, nameCap, nameCap))
            svc.set_options(wsse=self.my_security(self.username, self.password))
            svc.set_options(soapheaders=self.my_profile())
            svc.set_options(timeout=self.timeout)
            return svc

    def my_security(self, username, password):
        """Using username and password as key to verify user account to access avalara API's"""
        token = suds.wsse.UsernameToken(username, password)    
        token.setcreated(datetime.datetime.utcnow())            
        token.setnonce(self)                
        security = suds.wsse.Security()
        security.tokens.append(token)
        return security

    def my_profile(self):

        # Set elements adapter defaults
        ADAPTER = 'Odoo S.A.'

        # Profile Client.
        CLIENT = 'Odoo S.A.'

        #Build the Profile element
        profileNameSpace = ('ns1', 'http://avatax.avalara.com/services')
        profile = suds.sax.element.Element('Profile', ns=profileNameSpace)
        profile.append(suds.sax.element.Element('Client', ns=profileNameSpace).setText(CLIENT))
        profile.append(suds.sax.element.Element('Adapter', ns=profileNameSpace).setText(ADAPTER))
        hostname = socket.gethostname()
        profile.append(suds.sax.element.Element('Machine', ns=profileNameSpace).setText(hostname))
        return profile

    def get_result(self, svc, operation, request):
        try:
            result = operation(request)
#            print"result",result
        except suds.WebFault, e:
            raise UserError(_(e.fault.faultstring))
        except urllib2.HTTPError, e:
            raise UserError(_(e.code))
        except urllib2.URLError, details:
            # We could also print the SOAP request here:
            raise UserError(_(details.reason))
        else:
            if (result.ResultCode != 'Success'):
                #for w_message in result.Messages.Message:
#                w_message = result.Messages.Message[0]
                for w_message in result.Messages.Message:
#                    print"w_message",w_message
                    if w_message.Severity == 'Error':
                        if (w_message._Name == 'TaxAddressError' or w_message._Name == 'AddressRangeError' or  w_message._Name == 'AddressUnknownStreetError' or w_message._Name == 'AddressNotGeocodedError' or w_message._Name == 'NonDeliverableAddressError' ):
                            raise UserError(_('AvaTax: Warning AvaTax could not validate the street address. \n You can save the address and AvaTax will make an attempt to compute taxes based on the zip code if "Force Address Validation" is disabled in the Avatax connector configuration.  \n\n Also please ensure that the company address is set and Validated.  You can get there by going to Sales->Customers and removing "Customers" filter from the search at the top.  Then go to your company contact info and validate your address in the Avatax Tab'))
                        elif (w_message._Name == 'UnsupportedCountryError' ):
                            raise UserError(_("AvaTax: Notice\n\n Address Validation for this country not supported. But, Avalara will still calculate global tax rules."))
                        else:
                            raise UserError(_('AvaTax: Error: '+str(w_message._Name)+"\n\n" "Summary: " + w_message.Summary + "\n Details: " + str(w_message.Details or '') + "\n Severity: " + w_message.Severity))
            else:
                return result
            

    def ping(self):
        return self.get_result(self.taxSvc, self.taxSvc.service.Ping, '')

    def is_authorized(self):
        return self.get_result(self.taxSvc, self.taxSvc.service.IsAuthorized, 'GetTax,PostTax')
    
    def validate_address(self, baseaddress, textcase='Default'):
        request = self.addressSvc.factory.create('ValidateRequest')
        textCase = self.addressSvc.factory.create('TextCase')
        request.TextCase = textcase
        request.Coordinates = True
        request.Taxability = False
        request.Date = '2013-08-09'
        request.Address = baseaddress

        result = self.get_result(self.addressSvc, self.addressSvc.service.Validate, request)
        return result

    def get_tax(self, company_code, doc_date, doc_type, partner_code, doc_code, origin, destination,
               received_lines, exemption_no=None, customer_usage_type=None, salesman_code=None, commit=False, invoice_date=None, reference_code=None, 
               location_code=None, currency_code='USD', vat_id=None):
        """ Create tax request and get tax amount by customer address
            @currency_code : 'USD' is the default currency code for avalara, if user not specify in the own company
            @request.DetailLevel = 'Document': Document (GetTaxResult) level details; TaxLines will not be returned.
            @request.DetailLevel = 'Diagnostic': In addition to Tax level details, indicates that the server should 
            return information about how the tax was calculated. Intended for use only while the SDK is in a development environment.
        """
        lineslist = []
        request = self.taxSvc.factory.create('GetTaxRequest')
        request.Commit = commit
        request.DetailLevel = 'Diagnostic'
#        request.DetailLevel = 'Document'
        request.Discount = 0.0
        request.ServiceMode = 'Automatic'   ##service mode = Automatic/Local/Remote
        request.PaymentDate = doc_date
        request.ExchangeRate = 45
        request.ExchangeRateEffDate = fields.Date.today()
        request.HashCode = 0
        request.LocationCode = location_code
        request.ReferenceCode = reference_code
        if invoice_date:
            taxoverride = self.taxSvc.factory.create('TaxOverride')
            taxoverride.TaxOverrideType = 'TaxDate'
            taxoverride.TaxDate = invoice_date
            taxoverride.TaxAmount = 0
            taxoverride.Reason = 'Return Items'
            request.TaxOverride = taxoverride
       
        request.CompanyCode = company_code
        request.DocDate = doc_date
        request.DocType = doc_type
        request.DocCode = doc_code
        request.CustomerCode = partner_code
        request.ExemptionNo = exemption_no
        request.CustomerUsageType = customer_usage_type
        request.SalespersonCode = salesman_code
        request.CurrencyCode = currency_code
        request.BusinessIdentificationNo = vat_id
        
        addresses = self.taxSvc.factory.create('ArrayOfBaseAddress')
        addresses.BaseAddress = [origin, destination]
        if origin.Line1 == False:         
            raise UserError(_('Please set the Company Address in the partner information and validate.  We are checking against the first line of the address and it\'s empty.  \n\n Typically located in Sales->Customers, you have to clear "Customers" from search filter and type in your own company name.  Ensure the address is filled out and go to Avatax tab in the partner information and validate the address. Save partner update when done.'))
        request.Addresses = addresses
        request.OriginCode = '0' # Referencing an address above
        request.DestinationCode = '1' # Referencing an address above
        for line in range(0, len(received_lines)):
            line1 = self.taxSvc.factory.create('Line')
            line1.Qty = received_lines[line].get('qty', 1)
            line1.Discounted = False
            line1.No = '%d' %line
            line1.ItemCode = received_lines[line].get('itemcode', None)
            desc = received_lines[line].get('description', None)
            line1.Description = tools.ustr(desc)[:255]
            line1.Amount = received_lines[line].get('amount', 0.0)
            line1.TaxCode = received_lines[line].get('tax_code', None)
            lineslist.append(line1)
        # So now we build request.Lines
        lines = self.taxSvc.factory.create('ArrayOfLine')
        lines.Line = lineslist
        request.Lines = lines
        # And we're ready to make the call
        result = self.get_result(self.taxSvc, self.taxSvc.service.GetTax, request)
        return result
    
    def get_tax_history(self, company_code, doc_code, doc_type):
        request = self.taxSvc.factory.create('GetTaxHistoryRequest')
        request.DetailLevel = 'Document'
        request.CompanyCode = company_code
        request.DocCode = doc_code
        request.DocType = doc_type
#        request.CancelCode = cancel_code
        result = self.get_result(self.taxSvc, self.taxSvc.service.GetTaxHistory, request)
        return result
        

    def cancel_tax(self, company_code, doc_code, doc_type, cancel_code):
        request = self.taxSvc.factory.create('CancelTaxRequest')
        request.CompanyCode = company_code
        request.DocCode = doc_code
        request.DocType = doc_type
        request.CancelCode = cancel_code
        result = self.get_result(self.taxSvc, self.taxSvc.service.CancelTax, request)
        return result

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class AvaTaxError(Error):
    """Exception raised for errors calling AvaTax.

    Attributes:
        resultCode -- result.ResultCode
        messages  -- result.Messages
    """

    def __init__(self, resultCode, messages):
        self.resultCode = resultCode
        self.messages = messages
        self.__str__
        

    def __str__(self):
        output_str = ''
        for item in self.messages:
            message = item[1][0] # SUDS gives us the message in a list, in a tuple

            output_str = "Severity: %s\n\nDetails: %s\n\n RefersTo: %s\n\n Summary: %s" \
            % (message.Severity, message.Details, message.RefersTo, message.Summary)
        return output_str

class BaseAddress:

    def __init__(self, addSvc, Line1=None, Line2=None, City=None, PostalCode=None, Region=None, Country=None, AddressCode=None):
        self.data = addSvc.factory.create('BaseAddress')
        self.data.TaxRegionId = 0
        self.data.Line1 = Line1
        self.data.Line2 = Line2
        self.data.City = City
        self.data.PostalCode = PostalCode
        self.data.Region = Region
        self.data.Country = Country
        self.data.AddressCode = AddressCode

class Line:

    def __init__(self, taxSvc, ItemCode, Amount, Qty, Description=None, TaxCode=None):
        self.taxSvc = taxSvc
        # We're not setting No here
        self.data = self.defaultLine()
        self.data.ItemCode = ItemCode
        self.data.Amount = Amount
        self.data.Qty = Qty
        self.data.Description = Description
        self.data.TaxCode = TaxCode

    def defaultLine(self):
        line = self.taxSvc.factory.create('Line')
        line.Qty = 1
        line.Discounted = False
        return line

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: