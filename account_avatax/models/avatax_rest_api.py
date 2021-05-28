# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
import pprint
import socket

from odoo import _, fields, tools
from odoo.exceptions import UserError

try:
    from avalara import AvataxClient
except Exception:
    pass


_logger = logging.getLogger(__name__)


class AvaTaxRESTService:
    def __init__(
        self,
        username=None,
        password=None,
        url=None,
        timeout=300,
        enable_log=False,
        config=None,
    ):
        self.config = config
        self.timeout = not config and timeout or config.request_timeout
        self.is_log_enabled = enable_log or config and config.logging
        # Set elements adapter defaults
        self.appname = "Odoo 14, published by Odoo Community Association"
        self.version = "a0o5a0000064hvAAAQ"
        self.hostname = socket.gethostname()
        url = url or (config and config.service_url) or ""
        self.environment = (
            "sandbox" if "sandbox" in url or "development" in url else "production"
        )
        username = username or (config and config.account_number) or False
        password = password or (config and config.license_key) or False
        if username and password:
            try:
                self.client = AvataxClient(
                    self.appname, self.version, self.hostname, self.environment
                )
            except NameError:
                raise UserError(
                    _(
                        "AvataxClient is not available in your system. "
                        "Please contact your system administrator "
                        "to 'pip3 install Avalara'"
                    )
                )
            self.client.add_credentials(username, password)

    def _sanitize_text(self, text):
        res = (
            text.replace("/", "_-ava2f-_")
            .replace("+", "_-ava2b-_")
            .replace("?", "_-ava3f-_")
            .replace(" ", "%20")
        )
        return res

    def get_result(self, response, ignore_error=None):
        # To call from validate address and from compute tax
        result = response.json()
        if self.config and self.config.logging_response or self.is_log_enabled:
            _logger.info("Response\n" + pprint.pformat(result, indent=1))
        if result.get("messages") or result.get("error"):
            messages = result.get("messages") or result.get("error", {}).get("details")
            if ignore_error and messages and messages[0].get("number") == ignore_error:
                return messages[0]
            for w_message in messages:
                if w_message.get("severity") in ("Error", "Exception"):
                    if w_message.get("refersTo", "").startswith("Address"):
                        raise UserError(
                            _(
                                "AvaTax: Warning AvaTax could not validate the"
                                " address:\n%s\n\n"
                                "You can save the address and AvaTax will make an"
                                " attempt to "
                                "compute taxes based on the zip code if"
                                ' "Force Address Validation" is disabled '
                                "in the Avatax connector configuration.  \n\n "
                                "Also please ensure that the company address is"
                                " set and Validated.  "
                                "You can get there by going to Sales->Customers "
                                'and removing "Customers" filter from the search'
                                " at the top.  "
                                "Then go to your company contact info and validate"
                                " your address in the Avatax Tab"
                            )
                            % str(", ".join(result.get("address", {}).values()))
                        )
                    elif w_message.get("refersTo") == "Country":
                        raise UserError(
                            _(
                                "AvaTax: Notice\n\n Address Validation for this"
                                " country not supported. "
                                "But, Avalara will still calculate global tax"
                                " rules."
                            )
                        )
                    else:
                        message = "AvaTax: Error: "
                        if w_message.get("refersTo"):
                            message += str(w_message.get("refersTo")) + "\n\n"
                        elif w_message.get("code"):
                            message += str(w_message.get("code")) + "\n\n"
                        if w_message.get("summary"):
                            message += "Summary: " + str(w_message.get("summary"))
                        elif w_message.get("message"):
                            message += "Message: " + str(w_message.get("message"))
                        if w_message.get("details"):
                            message += "\n Details: " + str(
                                w_message.get("details", "")
                            )
                        elif w_message.get("description"):
                            message += "\n Description: " + str(
                                w_message.get("description", "")
                            )
                        message += "\n Severity: " + str(w_message.get("severity"))
                        raise UserError(_(message))
        return result

    def ping(self):
        response = self.client.ping()
        res = response.json()
        if self.config and self.config.logging or self.is_log_enabled:
            _logger.info(pprint.pformat(res, indent=1))
        if not res.get("authenticated"):
            raise UserError(_("The user or account could not be authenticated"))
        return res

    def validate_rest_address(
        self, street, street2, city, zip_code, state_code, country_code
    ):
        if self.config.disable_address_validation:
            raise UserError(
                _(
                    "The AvaTax Address Validation Service"
                    " is disabled by the administrator."
                    " Please make sure it's enabled for the address validation"
                )
            )
        supported_countries = [x.code for x in self.config.country_ids]
        if country_code and country_code not in supported_countries:
            raise UserError(
                _(
                    "The AvaTax Address Validation Service does not support"
                    " this country in the configuration,"
                    " please continue with your normal process."
                )
            )
        textcase = "Upper" if self.config.result_in_uppercase else "Mixed"
        partner_data = {
            "line1": street or "",
            "line2": street2 or "",
            "city": city or "",
            "postalCode": zip_code or "",
            "region": state_code or "",
            "country": country_code or "",
            "textcase": textcase,
        }
        response_partner = self.client.resolve_address(partner_data)
        partner_dict = self.get_result(response_partner)
        valid_address = partner_dict.get("validatedAddresses")[0]
        Partner = self.config.env["res.partner"]
        country = Partner.get_country_from_code(valid_address.get("country"))
        state = Partner.get_state_from_code(
            valid_address.get("region"), valid_address.get("country")
        )
        address_vals = {
            "street": valid_address.get("line1", ""),
            "street2": valid_address.get("line2", ""),
            "city": valid_address.get("city", ""),
            "zip": valid_address.get("postalCode", ""),
            "country_id": country.id,
            "state_id": state.id,
            "date_validation": fields.Date.today(),
            "validation_method": "avatax",
            "partner_latitude": valid_address.get("latitude"),
            "partner_longitude": valid_address.get("longitude"),
        }
        return address_vals

    def _enrich_result_lines_with_tax_rate(self, avatax_result):
        """
        Enrich Avatax result with Odoo tax computation.
        Tax details can have a tax rate with zero tax amount.
        In this case the tax rate should be ignored.

        result is a dict with a 'createTransactionModel' returned by Avatax
        """
        for line in avatax_result.get("lines", []):
            line["rate"] = (
                round(
                    sum(x["rate"] for x in line["details"] if x and x.get("tax")) * 100,
                    4,
                )
                or 0.0
            )
        return avatax_result

    def get_tax(
        self,
        company_code,
        doc_date,
        doc_type,
        partner_code,
        doc_code,
        origin,
        destination,
        received_lines,
        exemption_no=None,
        customer_usage_type=None,
        salesman_code=None,
        commit=False,
        invoice_date=None,
        reference_code=None,
        location_code=None,
        currency_code="USD",
        vat=None,
        is_override=False,
        ignore_error=None,
    ):
        """Create tax request and get tax amount by customer address
        @currency_code : 'USD' is the default currency code for avalara,
        if user not specify in the own company
        return information about how the tax was calculated.  Intended
        for use only while the SDK is in a development environment.
        """
        if not origin.street:
            raise UserError(
                _(
                    "Please set the Company Address "
                    "in the partner information and validate.  "
                    "We are checking against the first line of the address "
                    "and it's empty.  \n\n "
                    "Typically located in Sales->Customers, "
                    'you have to clear "Customers" '
                    "from search filter and type in your own company name.  "
                    "Ensure the address is filled out "
                    "and go to Avatax tab in the partner information "
                    "and validate the address. Save partner update when done."
                )
            )
        lineslist = [
            {
                "number": line["id"].id,
                "description": tools.ustr(line.get("description", ""))[:255],
                "itemCode": line.get("itemcode"),
                "quantity": line.get("qty", 1),
                "amount": line.get("amount", 0.0),
                "taxCode": line.get("tax_code"),
            }
            for line in received_lines
        ]

        if doc_date and type(doc_date) != str:
            doc_date = fields.Date.to_string(doc_date)
        create_transaction = {
            "addresses": {
                "shipFrom": {
                    "city": origin.city,
                    "country": origin.country_id.code or None,
                    "line1": origin.street or None,
                    "postalCode": origin.zip,
                    "region": origin.state_id.code or None,
                },
                "shipTo": {
                    "city": destination.city,
                    "country": destination.country_id.code or None,
                    "line1": destination.street or None,
                    "postalCode": destination.zip,
                    "region": destination.state_id.code or None,
                },
            },
            "lines": lineslist,
            # 'purchaseOrderNo": "2020-02-05-001"
            "companyCode": company_code,
            "currencyCode": currency_code,
            "customerCode": partner_code,
            "businessIdentificationNo": vat,
            "referenceCode": reference_code,
            "salespersonCode": salesman_code,
            "reportingLocationCode": location_code,
            "entityUseCode": customer_usage_type,
            "exemptionNo": exemption_no,
            "description": doc_code or "Draft",
            "date": doc_date,
            "code": doc_code,
            "type": doc_type,
            "commit": commit,
        }
        if is_override and invoice_date:
            create_transaction.update(
                {
                    "taxOverride": {
                        "type": "TaxDate",
                        "taxAmount": 0,
                        "taxDate": fields.Date.to_string(invoice_date),
                        "reason": "Return Items",
                    }
                }
            )

        data = {"createTransactionModel": create_transaction}
        if self.config and self.config.logging or self.is_log_enabled:
            _logger.info(
                "Request CreateOrAdjustTransaction %s %s (commit %s)\n%s",
                doc_type,
                doc_code,
                commit,
                pprint.pformat(data, indent=1),
            )

        response = self.client.create_or_adjust_transaction(data)
        result = self.get_result(response, ignore_error=ignore_error)
        return self._enrich_result_lines_with_tax_rate(result)

    def call(self, endpoint, company_code, doc_code, model=None, params=None):
        if self.config and self.config.logging or self.is_log_enabled:
            _logger.info(
                "Request Call %s(%s, %s, %s, %s)",
                endpoint,
                company_code,
                doc_code,
                model,
                params,
            )
        company_code = self._sanitize_text(company_code)
        doc_code = self._sanitize_text(doc_code)
        endpoint_method = getattr(self.client, endpoint)
        if params:
            response = endpoint_method(company_code, doc_code, model, params)
        else:
            response = endpoint_method(company_code, doc_code, model)
        result = self.get_result(response)
        return result
