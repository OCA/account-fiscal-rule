import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from .avatax_rest_api import AvaTaxRESTService


_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    """Inherit to implement the tax using avatax API"""

    _inherit = "account.tax"

    is_avatax = fields.Boolean("Is Avatax")

    @api.model
    def _get_compute_tax(
        self,
        avatax_config,
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
        invoice_date=False,
        reference_code=False,
        location_code=False,
        is_override=False,
        currency_id=False,
    ):
        currency_code = self.env.user.company_id.currency_id.name
        if currency_id:
            currency_code = currency_id.name

        if not partner.customer_code:
            if not avatax_config.auto_generate_customer_code:
                raise UserError(
                    _(
                        "Customer Code for customer %s not defined.\n\n  "
                        "You can edit the Customer Code in customer profile. "
                        'You can fix by clicking "Generate Customer Code" button in the customer contact information"'
                        % (partner.name)
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
            raise UserError(_("There is no company address defined."))

        # this condition is required, in case user select force address validation on AvaTax API Configuration
        if not avatax_config.address_validation:
            if avatax_config.force_address_validation:
                if not shipping_address.date_validation:
                    raise UserError(
                        _(
                            "Please validate the shipping address for the partner %s."
                            % (partner.name)
                        )
                    )

            # if not avatax_config.address_validation:
            if not ship_from_address.date_validation:
                raise UserError(_("Please validate the company address."))

        if avatax_config.disable_tax_calculation:
            _logger.info(
                "Avatax tax calculation is disabled. Skipping %s %s.",
                doc_code,
                doc_type,
            )
            return False

        if commit and avatax_config.disable_tax_reporting:
            _logger.warn(
                _("Avatax commiting document %s, " "but it tax reporting is disabled."),
                doc_code,
            )

        avatax_restpoint = AvaTaxRESTService(
            avatax_config.account_number,
            avatax_config.license_key,
            avatax_config.service_url,
            avatax_config.request_timeout,
            avatax_config.logging,
        )
        result = avatax_restpoint.get_tax(
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
            commit,
            invoice_date,
            reference_code,
            location_code,
            currency_code,
            partner.vat_id or None,
            is_override,
        )
        return result

    @api.model
    def cancel_tax(self, avatax_config, doc_code, doc_type, cancel_code):
        """Sometimes we have not need to tax calculation, then method is used to cancel taxation"""
        if avatax_config.disable_tax_calculation:
            _logger.info(
                "Avatax tax calculation is disabled. Skipping %s %s.",
                doc_code,
                doc_type,
            )
            return False

        avatax_restpoint = AvaTaxRESTService(
            avatax_config.account_number,
            avatax_config.license_key,
            avatax_config.service_url,
            avatax_config.request_timeout,
            avatax_config.logging,
        )
        result = avatax_restpoint.cancel_tax(
            avatax_config.company_code, doc_code, doc_type, cancel_code
        )
        return result
