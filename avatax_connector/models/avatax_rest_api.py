# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import collections
import socket
from avalara import AvataxClient
import logging
import pprint

from odoo import fields, tools, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class AvaTaxRESTService:
    def __init__(self, username, password, url, timeout, enable_log=False):
        self.timeout = timeout
        self.is_log_enabled = enable_log
        # Set elements adapter defaults
        self.appname = "Odoo, by Open Source Integrators"
        # Profile Client.
        # TODO: set on client Header the Appname and OSI Key
        self.CLIENT = "a0o0b0000058pOuAAI"
        self.version = "12.3.0.1"  # TODO: hardcoded or retrieved from Avatax?
        self.hostname = socket.gethostname()
        self.environment = "production"  # TODO: selction production|sandbox
        self.client = AvataxClient(
            self.appname, self.version, self.hostname, self.environment
        )
        if username and password:
            self.client.add_credentials(username, password)

    def get_result(self, response):
        # To call from validate address and from compute tax
        result = response.json()
        _logger.info(pprint.pformat(result, indent=1))
        if result.get("messages"):
            for w_message in result.get("messages"):
                if w_message.get("severity") == "Error":
                    if (
                        w_message.get("refersTo") == "Address"
                        or w_message.get("refersTo") == "Address.Line0"
                        or w_message.get("refersTo") == "Address.City"
                    ):
                        raise UserError(
                            _(
                                "AvaTax: Warning AvaTax could not validate the"
                                " street address. \n "
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
                        raise UserError(
                            _(
                                "AvaTax: Error: "
                                + str(w_message.get("refersTo"))
                                + "\n\n"
                                "Summary: "
                                + w_message.get("summary")
                                + "\n Details: "
                                + str(w_message.get("details", ""))
                                + "\n Severity: "
                                + w_message.get("severity")
                            )
                        )
        else:
            return result

    def ping(self):
        response = self.client.ping()
        res = response.json()
        if self.is_log_enabled:
            _logger.info(pprint.pformat(res, indent=1))
        if not res.get("authenticated"):
            raise UserError(_("The user or account could not be authenticated"))
        return res

    def validate_rest_address(self, address, state_code, country_code):
        partner_data = {
            "line1": address.get("street") or None,
            "line2": address.get("street2") or None,
            "city": address.get("city"),
            "region": state_code,
            "country": country_code,
            "postalCode": address.get("zip"),
        }
        response_partner = self.client.resolve_address(partner_data)
        partner_dict = self.get_result(response_partner)
        addresses_dict = partner_dict.get("validatedAddresses")[0]
        BaseAddress = collections.namedtuple(
            "BaseAddress",
            [
                "Line1",
                "Line2",
                "City",
                "PostalCode",
                "Country",
                "Region",
                "Latitude",
                "Longitude",
            ],
        )
        Address = BaseAddress(
            Line1=addresses_dict.get("line1"),
            Line2=addresses_dict.get("line2"),
            City=addresses_dict.get("city"),
            PostalCode=addresses_dict.get("city"),
            Country=addresses_dict.get("country"),
            Region=addresses_dict.get("region"),
            Latitude=addresses_dict.get("latitude"),
            Longitude=addresses_dict.get("longitude"),
        )
        return Address

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
        vat_id=None,
        is_override=False,
    ):
        """ Create tax request and get tax amount by customer address
            @currency_code : 'USD' is the default currency code for avalara,
            if user not specify in the own company
            return information about how the tax was calculated.  Intended
            for use only while the SDK is in a development environment.
        """
        if commit:
            _logger.info(
                "GetTaxrequest committing document %s (type: %s)", doc_code, doc_type
            )
        else:
            _logger.info("GetTaxRequest for document %s (type: %s)", doc_code, doc_type)
        lineslist = []
        if not origin.street:
            raise UserError(
                _(
                    "Please set the Company Address in the partner information and validate.  "
                    "We are checking against the first line of the address and it's empty.  \n\n "
                    'Typically located in Sales->Customers, you have to clear "Customers" '
                    "from search filter and type in your own company name.  "
                    "Ensure the address is filled out and go to Avatax tab in the partner information "
                    "and validate the address. Save partner update when done."
                )
            )
        for i, line in enumerate(received_lines):
            desc = line.get("description", None)
            line_dict = {
                "amount": line.get("amount", 0.0),
                "description": tools.ustr(desc)[:255],
                "itemCode": line.get("itemcode", None),
                "number": "%d" % (i + 1),
                "quantity": line.get("qty", 1),
                "taxCode": line.get("tax_code", None),
            }
            lineslist.append(line_dict)

        tax_document = {
            "addresses": {
                # 'SingleLocation': {'city': origin.city,
                #                     'country': origin.country_id.code or None,
                #                     'line1': origin.street or None,
                #                     'postalCode': origin.zip,
                #                     'region': origin.state_id.code or None
                #                     }
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
            "commit": commit,
            # 'purchaseOrderNo": "2020-02-05-001", Todo
            "companyCode": company_code,
            "currencyCode": currency_code,
            "customerCode": partner_code,
            "date": fields.Date.to_string(doc_date),
            "referenceCode": doc_code,
            "description": doc_code or "Draft",
            "lines": lineslist,
            "type": doc_type,
        }
        if is_override and invoice_date:
            tax_document.update(
                {
                    "taxOverride": {
                        "type": "TaxDate",
                        "taxAmount": 0,
                        "taxDate": fields.Date.to_string(invoice_date),
                        "reason": "Return Items",
                    }
                }
            )
        if self.is_log_enabled:
            _logger.info(pprint.pformat(tax_document, indent=1))
        response = self.client.create_transaction(tax_document)
        result = self.get_result(response)
        # This helps trace the source of redundant API calls
        if self.is_log_enabled:
            _logger.info(pprint.pformat(result, indent=1))
        Taxvalue = collections.namedtuple("Taxvalue", ["TotalTax"])
        tax_result = Taxvalue(TotalTax=result.get("totalTax"))
        return tax_result
