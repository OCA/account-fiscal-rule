import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .avatax_rest_api import AvaTaxRESTService

_logger = logging.getLogger(__name__)


class ExemptionCode(models.Model):
    _name = "exemption.code"
    _description = "Exemption Code"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code")

    @api.depends("name", "code")
    def name_get(self):
        def name(r):
            return r.code and "({}) {}".format(r.code, r.name) or r.name

        return [(r.id, name(r)) for r in self]


class AvalaraSalestax(models.Model):
    _name = "avalara.salestax"
    _description = "AvaTax Configuration"
    _rec_name = "account_number"

    @api.model
    def _get_avatax_supported_countries(self):
        """ Returns the countries supported by AvaTax Address Validation Service."""
        return self.env["res.country"].search([("code", "in", ["US", "CA"])])

    account_number = fields.Char(
        "Account Number", required=True, help="Account Number provided by AvaTax"
    )
    license_key = fields.Char(
        "License Key", required=True, help="License Key provided by AvaTax"
    )
    service_url = fields.Selection(
        [
            ("https://sandbox-rest.avatax.com/api/v2", "REST API Test"),
            ("https://rest.avatax.com/api/v2", "REST API Production"),
        ],
        string="Service URL",
        default="https://rest.avatax.com/api/v2",
        help="The url to connect with",
    )
    request_timeout = fields.Integer(
        "Request Timeout",
        default=300,
        help="Defines AvaTax request time out length"
        ", AvaTax best practices prescribes default setting of 300 seconds",
    )
    company_code = fields.Char(
        "Company Code",
        required=True,
        help="The company code as defined in the Admin Console of AvaTax",
    )
    logging = fields.Boolean(
        "Log API Request Details",
        help="Enables detailed AvaTax transaction logging within application",
    )
    logging_response = fields.Boolean(
        "Log API Response Details",
        help="Enables detailed AvaTax transaction logging within application",
    )
    result_in_uppercase = fields.Boolean(
        "Return validation results in upper case",
        help="Check is address validation results desired to be in upper case",
    )
    disable_address_validation = fields.Boolean(
        "Disable Address Validation", help="Check to disable address validation"
    )
    validation_on_save = fields.Boolean(
        "Automatic Address Validation",
        help="Automatically validates addresses when they are created or modified"
        " when Customer profile is saved.",
    )
    force_address_validation = fields.Boolean(
        "Require Validated Addresses",
        help="Only compute taxes if addresses were validated by the Avatax service",
    )
    auto_generate_customer_code = fields.Boolean(
        "Automatically generate missing customer code",
        default=True,
        help="This will generate customer code for the customer used in the "
        "transaction, if it doesn't have one already. "
        "Each code is unique per customer.  "
        "When this is disabled, you will have to manually go to each customer "
        "and manually generate their customer code.  "
        "This is required for Avatax and is only generated one time.",
    )
    disable_tax_calculation = fields.Boolean(
        "Disable AvaTax Calculation",
        help="No tax calculation requests will be sent to the AvaTax web service.",
        default=True,
    )
    disable_tax_reporting = fields.Boolean(
        "Disable Document Recording/Commiting",
        help="No transactions will be recorded in the Avatax service.",
    )
    enable_immediate_calculation = fields.Boolean(
        "Immediate AvaTax Calculation",
        help="Tax is computed immediately, as document lines are being added."
        " Warning: will cause heavy traffic on the Avatax service.",
    )
    default_shipping_code_id = fields.Many2one(
        "product.tax.code",
        "Default Shipping Code",
        help="The default shipping code which will be passed to Avalara",
    )
    country_ids = fields.Many2many(
        "res.country",
        "avalara_salestax_country_rel",
        "avalara_salestax_id",
        "country_id",
        "Countries",
        default=_get_avatax_supported_countries,
        help="Countries where address validation will be used",
    )
    active = fields.Boolean(
        "Active",
        default=True,
        help="Uncheck the active field to hide the record",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda self: self.env.company,
        help="Company which has subscribed to the AvaTax service",
    )
    upc_enable = fields.Boolean(
        "Enable UPC Taxability",
        help="Allows ean13 to be reported in place of Item Reference"
        " as upc identifier.",
    )
    invoice_calculate_tax = fields.Boolean(
        "Auto Calculate Tax on Invoice Save",
        help="Automatically triggers API to calculate tax If changes made on"
        "Invoice's warehouse_id, tax_on_shipping_address, "
        "Invoice line's price_unit, discount, quantity",
    )
    use_so_partner_id = fields.Boolean(
        string="Use Sale Customer Code on Invoice",
        help="If Boolean is checked, SO Partner Customer Code "
        "on Invoice will be used",
    )
    # TODO: add option to Display Prices with Tax Included

    # constraints on uniq records creation with account_number and company_id
    _sql_constraints = [
        (
            "code_company_uniq",
            "unique (company_code)",
            "Avalara setting is already available for this company code",
        ),
        (
            "account_number_company_uniq",
            "unique (account_number, company_id)",
            "The account number must be unique per company!",
        ),
    ]

    def get_avatax_rest_service(self):
        self.ensure_one()
        if self.disable_tax_calculation:
            _logger.info(
                "Avatax tax calculation is disabled, skipping Avatax API contact."
            )
            return False
        return AvaTaxRESTService(
            self.account_number,
            self.license_key,
            self.service_url,
            self.request_timeout,
            self.logging,
            config=self,
        )

    def create_transaction(
        self,
        doc_date,
        doc_code,
        doc_type,
        partner,
        ship_from_address,
        shipping_address,
        lines,
        user=None,
        exemption_number=None,
        exemption_code_name=None,
        commit=False,
        invoice_date=None,
        reference_code=None,
        location_code=None,
        is_override=None,
        currency_id=None,
        ignore_error=None,
    ):
        self.ensure_one()
        avatax_config = self

        currency_code = self.env.user.company_id.currency_id.name
        if currency_id:
            currency_code = currency_id.name

        if not partner.customer_code:
            if not avatax_config.auto_generate_customer_code:
                raise UserError(
                    _(
                        "Customer Code for customer %s not defined.\n\n  "
                        "You can edit the Customer Code in customer profile. "
                        'You can fix by clicking "Generate Customer Code" '
                        "button in the customer contact information" % (partner.name)
                    )
                )
            else:
                partner.generate_cust_code()

        if not shipping_address:
            raise UserError(
                _("There is no source shipping address defined for partner %s.")
                % partner.name
            )

        if not ship_from_address:
            raise UserError(_("There is no Company address defined."))

        if avatax_config.validation_on_save:
            for address in [partner, shipping_address, ship_from_address]:
                if not address.date_validation:
                    address.multi_address_validation()

        # this condition is required, in case user select force address validation
        # on AvaTax API Configuration
        if (
            avatax_config.force_address_validation
            and not avatax_config.disable_address_validation
        ):
            if not shipping_address.date_validation:
                raise UserError(
                    _(
                        "Please validate the shipping address for the partner %s."
                        % (partner.name)
                    )
                )

            # if not avatax_config.address_validation:
            if not ship_from_address.date_validation:
                raise UserError(_("Please validate the origin warehouse address."))

        if avatax_config.disable_tax_calculation:
            _logger.info(
                "Avatax tax calculation is disabled. Skipping %s %s.",
                doc_code,
                doc_type,
            )
            return False

        if commit and avatax_config.disable_tax_reporting:
            _logger.warn(
                _("Avatax commiting document %s, but it tax reporting is disabled."),
                doc_code,
            )

        avatax = self.get_avatax_rest_service()
        result = avatax.get_tax(
            avatax_config.company_code,
            doc_date,
            doc_type,
            partner.customer_code,
            doc_code,
            ship_from_address,
            shipping_address,
            lines,
            exemption_number,
            exemption_code_name,
            user and user.name or None,
            commit and not avatax_config.disable_tax_reporting,
            invoice_date,
            reference_code,
            location_code,
            currency_code,
            partner.vat or None,
            is_override,
            ignore_error=ignore_error,
        )
        return result

    def commit_transaction(self, doc_code, doc_type):
        self.ensure_one()
        result = False
        if not self.disable_tax_reporting:
            avatax = self.get_avatax_rest_service()
            result = avatax.call(
                "commit_transaction", self.company_code, doc_code, {"commit": True}
            )
        return result

    def void_transaction(self, doc_code, doc_type):
        if self:
            self.ensure_one()
            result = False
            if not self.disable_tax_reporting:
                avatax = self.get_avatax_rest_service()
                result = avatax.call(
                    "void_transaction",
                    self.company_code,
                    doc_code,
                    {"code": "DocVoided"},
                )
            return result

    def unvoid_transaction(self, doc_code, doc_type):
        self.ensure_one()
        result = False
        if not self.disable_tax_reporting:
            avatax = self.get_avatax_rest_service()
            result = avatax.call("unvoid_transaction", self.company_code, doc_code)
        return result

    def ping(self):
        avatax_restpoint = AvaTaxRESTService(config=self)
        avatax_restpoint.ping()
        return True
