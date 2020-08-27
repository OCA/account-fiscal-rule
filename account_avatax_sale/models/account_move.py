from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        self._onchange_partner_shipping_id()
        return res

    @api.onchange("partner_shipping_id")
    def _onchange_partner_shipping_id(self):
        res = super(AccountMove, self)._onchange_partner_shipping_id()
        if not self.exemption_locked:
            invoice_partner = self.partner_id.commercial_partner_id
            ship_to_address = self.shipping_add_id
            # Find an exemption address matching the Country + State
            # of the Delivery address
            exemption_addresses = (
                invoice_partner | invoice_partner.child_ids
            ).filtered("property_tax_exempt")
            exemption_address_naive = exemption_addresses.filtered(
                lambda a: a.country_id == ship_to_address.country_id
                and (
                    a.state_id == ship_to_address.state_id
                    or invoice_partner.property_exemption_country_wide
                )
            )[:1]
            # Force Company to get the correct values form the Property fields
            exemption_address = exemption_address_naive.with_context(
                force_company=self.company_id.id
            )
            self.exemption_code = exemption_address.property_exemption_number
            self.exemption_code_id = exemption_address.property_exemption_code_id

        self.tax_on_shipping_address = bool(self.partner_shipping_id)
        self.is_add_validate = bool(self.partner_shipping_id.validation_method)
        return res
