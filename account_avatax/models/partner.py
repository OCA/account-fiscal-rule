import logging
import time
from random import random

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .avatax_rest_api import AvaTaxRESTService

_LOGGER = logging.getLogger(__name__)


class ResPartner(models.Model):
    """
    Update partner information by adding new fields
    according to Avalara partner configuration
    """

    _inherit = "res.partner"

    exemption_number = fields.Char(
        "Exemption Number", help="Indicates if the customer is exempt or not"
    )
    exemption_code_id = fields.Many2one(
        "exemption.code",
        "Exemption Code",
        help="Indicates the type of exemption the customer may have",
    )
    date_validation = fields.Date(
        "Last Validation Date",
        readonly=True,
        help="The date the address was last validated by AvaTax and accepted",
    )
    validation_method = fields.Selection(
        [("avatax", "AVALARA"), ("usps", "USPS"), ("other", "Other")],
        "Address Validation Method",
        readonly=True,
        help="It gets populated when the address is validated by the method",
    )
    validated_on_save = fields.Boolean(
        "Validated On Save",
        help="Indicates if the address is already validated on save"
        " before calling the wizard",
    )
    customer_code = fields.Char("Customer Code")
    tax_exempt = fields.Boolean(
        "Is Tax Exempt", help="Indicates the exemption tax calculation is compulsory"
    )

    _sql_constraints = [
        ("name_uniq", "unique(customer_code)", "Customer Code must be unique!"),
    ]

    @api.depends("tax_exempt", "exemption_code_id", "exemption_number")
    def check_exemption_number(self):
        """
        When tax exempt check then atleast exemption number
        or exemption code should be filled
        """
        for partner in self:
            if partner.tax_exempt and not (
                partner.exemption_code_id or partner.exemption_number
            ):
                raise UserError(
                    _(
                        "Please enter either Exemption Number or Exemption Code"
                        " for marking customer as Exempt."
                    )
                )

    def _get_avatax_customer_code(self):
        self.ensure_one()
        return "%d-%d-Cust-%d" % (int(time.time()), int(random() * 10), self.id,)

    def generate_cust_code(self):
        "Auto populate customer code"
        for partner in self:
            partner.customer_code = partner._get_avatax_customer_code()
        return True

    @api.onchange("tax_exempt")
    def onchange_tax_exemption(self):
        if not self.tax_exempt:
            self.exemption_number = ""
            self.exemption_code_id = None

    def get_state_from_code(self, state_code, country_code):
        """ Returns the state from the code. """
        state = self.env["res.country.state"].search(
            [("code", "=", state_code), ("country_id.code", "=", country_code)],
        )
        return state

    def get_country_from_code(self, code):
        """ Returns the country from the code. """
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
                partner.name,
            )
            return False
        company = partner.company_id or self.env.user.company_id
        avatax_config = company.get_avatax_config_company()
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
                valid_address = self.get_valid_address_vals(
                    validation_on_save=validation_on_save
                )
                if valid_address:
                    partner.write(valid_address)
        return True

    def button_avatax_validate_address(self):
        """Method is used to verify of state and country """
        view_ref = self.env.ref("account_avatax.view_avalara_salestax_address_validate")
        ctx = self.env.context.copy()
        ctx.update({"active_ids": self.ids, "active_id": self.id})
        return {
            "type": "ir.actions.act_window",
            "name": "Address Validation",
            "binding_view_types": "form",
            "view_mode": "form",
            "view_id": view_ref.id,
            "res_model": "avalara.salestax.address.validate",
            "nodestroy": True,
            "res_id": False,
            "target": "new",
            "context": ctx,
        }

    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)
        # Auto populate customer code
        partner.generate_cust_code()
        # Auto validate address, if enabled
        company = partner.company_id or self.env.user.company_id
        avatax_config = company.get_avatax_config_company()
        if avatax_config.validation_on_save:
            partner.multi_address_validation(validation_on_save=True)
            partner.validated_on_save = True
        return partner

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        address_fields = ["street", "street2", "city", "zip", "state_id", "country_id"]
        if not self.env.context.get("avatax_writing") and any(
            x in vals for x in address_fields
        ):
            partner = self.with_context(avatax_writing=True)
            company = partner.company_id or self.env.user.company_id
            avatax_config = company.get_avatax_config_company()
            if avatax_config.validation_on_save:
                partner.multi_address_validation(validation_on_save=True)
                partner.validated_on_save = True
        return res
