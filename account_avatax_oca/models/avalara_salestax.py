import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

from .avatax_rest_api import AvaTaxRESTService

_logger = logging.getLogger(__name__)


class ExemptionCode(models.Model):
    _name = "exemption.code"
    _description = "Exemption Code"

    name = fields.Char(required=True)
    code = fields.Char()

    @api.depends("name", "code")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for exemption in self:
            exemption.display_name = (
                exemption.code
                and f"({exemption.code}) {exemption.name}"
                or exemption.name
            )
        return res


class AvalaraSalestax(models.Model):
    _name = "avalara.salestax"
    _description = "AvaTax Configuration"
    _rec_name = "account_number"

    @api.model
    def _get_avatax_supported_countries(self):
        """Returns the countries supported by AvaTax Address Validation Service."""
        return self.env["res.country"].search([("code", "in", ["US", "CA"])])

    account_number = fields.Char(
        name="Account ID", required=True, help="Account Number provided by AvaTax"
    )
    license_key = fields.Char(required=True, help="License Key provided by AvaTax")
    service_url = fields.Selection(
        [
            ("https://rest.avatax.com/api/v2", "Production (REST API)"),
            ("https://sandbox-rest.avatax.com/api/v2", "Sandbox (REST API)"),
        ],
        string="Service URL",
        default="https://rest.avatax.com/api/v2",
        help="The url to connect with",
    )
    request_timeout = fields.Integer(
        default=300,
        help="Defines AvaTax request time out length"
        ", AvaTax best practices prescribes default setting of 300 seconds",
    )
    company_code = fields.Char(
        default="DEFAULT",
        required=True,
        help="The company code as defined in the Admin Console of AvaTax",
    )
    logging = fields.Boolean(
        "Log API Requests",
        help="Enables detailed AvaTax transaction logging within application",
    )
    result_in_uppercase = fields.Boolean(
        "Return validation results in upper case",
        help="The address validation results are returned in in upper case",
    )
    disable_address_validation = fields.Boolean(
        help="Disables the ability to perform address validation"
    )
    validation_on_save = fields.Boolean(
        "Automatic Address Validation",
        help="Automatically validates addresses when they are created or modified",
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
    )
    # TODO: Control - Disable Document Recording
    # In order for this connector to be used in conjunction with other integrations to
    # AvaTax, the user must be able to control which connector
    # is used for recording documents to AvaTax.
    # From a technical standpoint, simply use DocType: 'SalesOrder' on all calls
    # and suppress any non-getTax calls (i.e. cancelTax, postTax).
    disable_tax_reporting = fields.Boolean(
        "Disable Document Recording/Commiting",
        help="No transactions will be recorded (commited) to the Avatax service.",
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
    company_partner_id = fields.Many2one(
        string="Company Address",
        related="company_id.partner_id",
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
        help="Use Sales Order's Customer field to determine Taxable "
        "Status on the Customer Invoice. If no Sales Order exists, "
        "Customer field on the invoice form view will be used instead",
    )
    hide_exemption = fields.Boolean(
        "Hide Exemption & Tax Based on shipping address",
        default=False,
        help="Uncheck the this field to show exemption fields on SO/Invoice form view. "
        "Also, it will show Tax based on shipping address button",
    )
    # TODO: add option to Display Prices with Tax Included
    # Enabled the tax inclusive flag in the GetTax Request.

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
        log_to_record=False,
    ):
        self.ensure_one()
        avatax_config = self

        currency_code = self.env.company.currency_id.name
        if currency_id:
            currency_code = currency_id.name

        if not partner.customer_code:
            if not avatax_config.auto_generate_customer_code:
                raise UserError(
                    self.env._(
                        "Customer Code for customer %(partner.name)s not defined.\n\n  "
                        "You can edit the Customer Code in customer profile. "
                        'You can fix by clicking "Generate Customer Code" '
                        "button in the customer contact information"
                    )
                )
            else:
                partner.generate_cust_code()

        if not shipping_address:
            raise UserError(
                self.env._(
                    "There is no source shipping address defined for partner %s."
                )
                % partner.name
            )

        if not ship_from_address:
            raise UserError(self.env._("There is no Company address defined."))

        if avatax_config.validation_on_save:
            for address in [partner, shipping_address, ship_from_address]:
                if not address.date_validation:
                    address.multi_address_validation(validation_on_save=True)

        # this condition is required, in case user select force address validation
        # on AvaTax API Configuration
        if (
            avatax_config.force_address_validation
            and not avatax_config.disable_address_validation
        ):
            if not shipping_address.date_validation:
                raise UserError(
                    self.env._(
                        "Please validate the shipping address for the partner "
                        "%(partner.name)s."
                    )
                )

            # if not avatax_config.address_validation:
            if not ship_from_address.date_validation:
                raise UserError(
                    self.env._("Please validate the origin warehouse address.")
                )

        if avatax_config.disable_tax_calculation:
            _logger.info(
                self.env._("Avatax tax calculation is disabled. Skipping %s %s."),
                doc_code,
                doc_type,
            )
            return False

        if commit and avatax_config.disable_tax_reporting:
            _logger.warning(
                self.env._(
                    "Avatax commiting document %s, but it tax reporting is disabled."
                ),
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
            log_to_record=log_to_record,
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
        client = AvaTaxRESTService(config=self)
        client.ping()
        return True
