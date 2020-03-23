from odoo import api, fields, models


class ExemptionCode(models.Model):
    _name = 'exemption.code'
    _description = 'Exemption Code'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')

    @api.depends('name', 'code')
    def name_get(self):
        def name(r): return r.code and '(%s) %s' % (r.code, r.name) or r.name
        return [(r.id, name(r)) for r in self]


class AvalaraSalestax(models.Model):
    _name = 'avalara.salestax'
    _description = 'AvaTax Configuration'
    _rec_name = 'account_number'

    @api.model
    def _get_avatax_supported_countries(self):
        """ Returns the countries supported by AvaTax Address Validation Service."""
        return self.env['res.country'].search([('code', 'in', ['US', 'CA'])])

    @api.onchange('on_order')
    def onchange_system_call1(self):
        if self.on_order:
            self.on_order = self.on_order
            self.on_line = False

    @api.onchange('on_line')
    def onchange_system_call2(self):
        if self.on_line:
            self.on_order = False
            self.on_line = self.on_line

    account_number = fields.Char(
        'Account Number', required=True, help="Account Number provided by AvaTax")
    license_key = fields.Char(
        'License Key', required=True, help="License Key provided by AvaTax")
    service_url = fields.Selection(
        [('https://development.avalara.net', 'Test'),
         ('https://avatax.avalara.net', 'Production')],
        string='Service URL',
        default='https://development.avalara.net',
        required=True,
        help="The url to connect with")
    date_expiration = fields.Date(
        'Service Expiration Date', readonly=True, help="The expiration date of the service")
    request_timeout = fields.Integer(
        'Request Timeout', default=300, help="Defines AvaTax request time out length, AvaTax best practices prescribes default setting of 300 seconds")
    company_code = fields.Char('Company Code', required=True,
                               help="The company code as defined in the Admin Console of AvaTax")
    logging = fields.Boolean(
        'Enable Logging', help="Enables detailed AvaTax transaction logging within application")
    address_validation = fields.Boolean(
        'Disable Address Validation', help="Check to disable address validation")
    enable_address_validation = fields.Boolean(
        'Enable Address Validation', help="Check to Enable address validation")
    result_in_uppercase = fields.Boolean('Return validation results in upper case',
                                         help="Check is address validation results desired to be in upper case")
    validation_on_save = fields.Boolean('Address Validation on save for customer profile',
                                        help="Validates the address and automatically saves when Customer profile is saved.")
    force_address_validation = fields.Boolean(
        'Force Address Validation', help="Check if address validation should be done before tax calculation")
    auto_generate_customer_code = fields.Boolean(
        'Automatically generate customer code', default=True,
        help="This will generate customer code for customers in the system who do not have codes already created.  "
        "Each code is unique per customer.  "
        "When this is disabled, you will have to manually go to each customer "
        "and manually generate their customer code.  "
        "This is required for Avatax and is only generated one time.")
    disable_tax_calculation = fields.Boolean(
        'Disable AvaTax Calculation',
        help="No tax calculation requests will be sent to the AvaTax web service.",
        default=True,
    )
    disable_tax_reporting = fields.Boolean(
        'Disable Avalara Tax Commit',
        help="Validated Invoices won't be set to Committed status on the Avalara service.",
    )
    enable_immediate_calculation = fields.Boolean(
        'Immediate AvaTax Calculation',
        help="Tax is computed immediately, as document lines are being added."
        " Warning: will cause heavy traffic on the Avatax service.",
    )
    default_shipping_code_id = fields.Many2one(
        'product.tax.code', 'Default Shipping Code',
        help="The default shipping code which will be passed to Avalara")
    country_ids = fields.Many2many(
        'res.country', 'avalara_salestax_country_rel', 'avalara_salestax_id', 'country_id', 'Countries',
        default=_get_avatax_supported_countries,
        help="Countries where address validation will be used")
    active = fields.Boolean('Active', default=True,
                            help="Uncheck the active field to hide the record")
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env['res.company']._get_main_company(),
        help="Company which has subscribed to the AvaTax service")
    on_line = fields.Boolean(
        'Line-level', help="It will calculate tax line by line and also show.")
    on_order = fields.Boolean('Order-level', default=True,
                              help="It will calculate tax for order not line by line.")
    upc_enable = fields.Boolean(
        'Enable UPC Taxability', help="Allows ean13 to be reported in place of Item Reference as upc identifier.")

    # constraints on uniq records creation with account_number and company_id
    _sql_constraints = [
        ('code_company_uniq', 'unique (company_code)',
         'Avalara setting is already available for this company code'),
        ('account_number_company_uniq', 'unique (account_number, company_id)',
         'The account number must be unique per company!'),
    ]
