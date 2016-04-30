# -*- coding: utf-8 -*-

{
    "name" : "Avalara Avatax Connector",
    "version" : "1.0",
    "author" : "Odoo S.A.",
    "summary": "Sales tax Calculation",
    "description": """ 
    
The Avatax module automates the complex task of sales tax calculation with ease.  Sale tax calculations are based on prevalidated shop, warehouse and customer address.  This app plugs into your current installation of odoo with minimal configuration and just works.  Your sales orders, invoices and refunds activity is automatically calculated from Avalara's calc service returning the proper sales tax and places the tax into the order/invoice seamlessly.  
 
This module has Following Features:

1. Customer and Company Address Validation
2. Line or Total Order amount sale tax calculation 
3. Handling of Customer Refunds
4. Customer Exemption handling
5. Calculation of Shipping Cost tax
6. Use both Avalara and Odoo Taxes etc
7. International support
8. Discount management
9. Reporting record through an avalara management console to verify transactions
10. Documentation included

""",
    "category" : "Generic Modules/Accounting",
    "website" : "https://www.odoo.com/",
    "depends" : [ 'base','account_accountant','sale'],
    "data" : [
    "security/avalara_salestax_security.xml",
    "security/ir.model.access.csv",
    "wizard/avalara_salestax_ping_view.xml",
    "wizard/avalara_salestax_address_validate_view.xml",
    "views/avalara_salestax_view.xml",
    "views/avalara_salestax_data.xml",
    "views/partner_view.xml",
    "views/product_view.xml",
    "views/account_invoice_workflow.xml",
    "views/account_invoice_view.xml",
    "views/sale_order_view.xml",
    "views/account_tax_view.xml",
#    "views/demo.xml",
    ],
    'demo': [
        
    ],    
    "test" : [],
    'images': [
        'static/description/avatax.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
   

    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
