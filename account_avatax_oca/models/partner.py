import logging
import time
from random import random

from odoo import api, fields, models
from odoo.exceptions import UserError

from .avatax_rest_api import AvaTaxRESTService

_LOGGER = logging.getLogger(__name__)


class ResPartner(models.Model):
    """
    Update partner information by adding new fields
    according to Avalara partner configuration
    """

    _inherit = "res.partner"

    @api.onchange("property_exemption_country_wide")
    def _onchange_property_exemption_contry_wide(self):
        if self.property_exemption_country_wide:
            message = self.env._(
                "Enabling the exemption status for all states"
                " may have tax compliance risks,"
                " and should be carefully considered.\n\n"
                " Please ensure that your tax advisor was consulted and the"
                " necessary tax exemption documentation was obtained"
                " for every state this Partner may have transactions."
            )
            return {
                "warning": {
                    "title": self.env._("Tax Compliance Risk"),
                    "message": message,
                }
            }

    date_validation = fields.Date(
        "Last Validation Date",
        readonly=True,
        copy=False,
        help="The date the address was last validated by AvaTax and accepted",
    )
    validation_method = fields.Selection(
        [("avatax", "Avalara"), ("other", "Other")],
        "Address Validation Method",
        readonly=True,
        copy=False,
        help="It gets populated when the address is validated by the method",
    )
    validated_on_save = fields.Boolean(
        help="Indicates if the address is already validated on save"
        " before calling the wizard",
    )
    customer_code = fields.Char(copy=False)
    tax_exempt = fields.Boolean(
        "Is Tax Exempt (Deprecated))",
    )
    exemption_number = fields.Char(
        "Exemption Number (Deprecated)",
    )
    exemption_code_id = fields.Many2one(
        "exemption.code",
        "Exemption Code (Deprecated)",
    )
    property_exemption_country_wide = fields.Boolean(
        "Exemption Applies Country Wide",
        help="When enabled, the delivery address State is irrelevant"
        " when looking up the exemption status, meaning that the exemption"
        " is considered applicable for all states",
    )
    property_tax_exempt = fields.Boolean(
        "Is Tax Exempt",
        company_dependent=True,
        help="This company or address can claim for tax exemption",
    )
    property_exemption_number = fields.Char(
        "Exemption Number",
        company_dependent=True,
        help="The State identification number relevant fot the exemption",
    )
    property_exemption_code_id = fields.Many2one(
        "exemption.code",
        "Exemption Code",
        company_dependent=True,
        help="The type of exemption granted",
    )

    _sql_constraints = [
        ("name_uniq", "unique(customer_code)", "Customer Code must be unique!"),
    ]

    @api.depends(
        "property_tax_exempt", "property_exemption_code_id", "property_exemption_number"
    )
    def check_exemption_number(self):
        """
        When tax exempt check then at least exemption number
        or exemption code should be filled
        """
        for partner in self:
            if partner.property_tax_exempt and not (
                partner.property_exemption_code_id or partner.property_exemption_number
            ):
                raise UserError(
                    self.env._(
                        "Please enter either Exemption Number or Exemption Code"
                        " for marking customer as Exempt."
                    )
                )

    def _get_avatax_customer_code(self):
        self.ensure_one()
        return "%d-%d-Cust-%d" % (
            int(time.time()),
            int(random() * 10),
            self.id,
        )

    def generate_cust_code(self):
        "Auto populate customer code"
        for partner in self:
            partner.customer_code = partner._get_avatax_customer_code()
        return True

    @api.onchange("tax_exempt")
    def onchange_tax_exemption(self):
        if not self.property_tax_exempt:
            self.property_exemption_number = ""
            self.property_exemption_code_id = None

    def get_state_from_code(self, state_code, country_code):
        """Returns the state from the code."""
        state = self.env["res.country.state"].search(
            [("code", "=", state_code), ("country_id.code", "=", country_code)],
        )
        return state

    def get_country_from_code(self, code):
        """Returns the country from the code."""
        country = self.env["res.country"].search([("code", "=", code)])
        return country

    def get_valid_address_vals(self, validation_on_save=False):
        self.ensure_one()
        partner = self
        # For automatic validation on save, skip
        # if no relevant address details are given
        if validation_on_save and not (
            partner.city or partner.zip or partner.country_id
        ):
            _LOGGER.info(
                "Skipping address validation for %d %s, not enough details.",
                partner.id,
                partner.display_name,
            )
            return False
        avatax_config = self.env.company.get_avatax_config_company()
        # Skip automatic validation for countries not supported by Avatax
        supported_countries = [x.code for x in avatax_config.country_ids]
        country_code = partner.country_id.code
        if validation_on_save and country_code not in supported_countries:
            _LOGGER.info(
                "Skipping automatic address validation for %d %s"
                ", country %s not supported.",
                partner.id,
                partner.display_name,
                country_code,
            )
            return False
        avatax_restpoint = AvaTaxRESTService(config=avatax_config)
        valid_address = avatax_restpoint.validate_rest_address(
            partner.street,
            partner.street2,
            partner.city,
            partner.zip,
            partner.state_id.code,
            partner.country_id.code,
        )
        return valid_address

    def multi_address_validation(self, validation_on_save=False):
        for partner in self:
            if not (partner.parent_id and partner.type == "contact"):
                valid_address = partner.get_valid_address_vals(
                    validation_on_save=validation_on_save
                )
                if valid_address:
                    partner.write(valid_address)
        return True

    def button_avatax_validate_address(self):
        """Method is used to verify of state and country"""
        view_ref = self.env.ref(
            "account_avatax_oca.view_avalara_salestax_address_validate"
        )
        ctx = self.env.context.copy()
        ctx.update({"active_ids": self.ids, "active_id": self.id})
        return {
            "type": "ir.actions.act_window",
            "name": "Address Validation",
            "binding_view_types": "form",
            "view_mode": "form",
            "view_id": view_ref.id,
            "res_model": "avalara.salestax.address.validate",
            # "nodestroy": True, TODO: not needed
            "res_id": False,
            "target": "new",
            "context": ctx,
        }

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        avatax_config = self.env.company.get_avatax_config_company()
        for partner in partners:
            # Auto populate customer code, if not provided
            if not partner.customer_code:
                partner.generate_cust_code()
            # Auto validate address, if enabled
            if avatax_config.validation_on_save:
                partner.multi_address_validation(validation_on_save=True)
                partner.validated_on_save = True
        return partners

    def write(self, vals):
        res = super().write(vals)
        address_fields = ["street", "street2", "city", "zip", "state_id", "country_id"]
        if not self.env.context.get("avatax_writing") and any(
            x in vals for x in address_fields
        ):
            partner = self.with_context(avatax_writing=True)
            avatax_config = self.env.company.get_avatax_config_company()
            if avatax_config.validation_on_save:
                partner.multi_address_validation(validation_on_save=True)
                partner.validated_on_save = True
        return res
