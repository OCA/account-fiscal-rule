from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_shipping_id")
    def _onchange_partner_shipping_id(self):
        """
        Apply Exemption code from delivery address, is available.
        Otherwise, use Customer company exempltion code.
        Note that partner_shippind_id is introduced by the ``sale`` module.
        """
        res = super()._onchange_partner_shipping_id()
        if not self.exemption_locked:
            self.exemption_code = (
                self.partner_shipping_id.exemption_number
                or self.partner_id.exemption_number
            )
            self.exemption_code_id = (
                self.partner_shipping_id.exemption_code_id
                or self.partner_id.exemption_code_id.id
            )
        self.tax_on_shipping_address = bool(self.partner_shipping_id)
        self.is_add_validate = bool(self.partner_shipping_id.validation_method)
        return res
