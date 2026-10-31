from odoo import api, fields, models


class AvalaraSalestaxAddressValidate(models.TransientModel):
    """Address Validation using Avalara API"""

    _name = "avalara.salestax.address.validate"
    _description = "Address Validation using AvaTax"

    original_street = fields.Char(readonly=True)
    original_street2 = fields.Char(readonly=True)
    original_city = fields.Char(readonly=True)
    original_zip = fields.Char(readonly=True)
    original_state = fields.Char(readonly=True)
    original_country = fields.Char(readonly=True)
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    zip = fields.Char()
    state = fields.Char()
    country = fields.Char()
    partner_latitude = fields.Float("Latitude")
    partner_longitude = fields.Float("Longitude")
    date_validation = fields.Date()
    validation_method = fields.Char()

    @api.model
    def default_get(self, fields):
        """Returns the default values for the fields."""
        res = super().default_get(fields)
        active_id = self.env.context.get("active_id")
        if active_id:
            Partner = self.env["res.partner"]
            address = Partner.browse(active_id)
            res.update(
                {
                    "original_street": address.street,
                    "original_street2": address.street2,
                    "original_city": address.city,
                    "original_zip": address.zip,
                    "original_state": address.state_id.code,
                    "original_country": address.country_id.code,
                }
            )
            valid_address = address.get_valid_address_vals()
            state_id = valid_address.pop("state_id", 0)
            state = self.env["res.country.state"].browse(state_id)
            country_id = valid_address.pop("country_id", 0)
            country = self.env["res.country"].browse(country_id)
            res.update(valid_address)
            res.update({"state": state.code, "country": country.code})
        return res

    def accept_valid_address(self):
        """
        Updates the existing address with the valid address
        returned by the service.
        """
        active_id = self.env.context.get("active_id")
        if active_id:
            Partner = self.env["res.partner"].with_context(avatax_writing=True)
            address = Partner.browse(active_id)
            vals = {
                "street": self.street,
                "street2": self.street2,
                "city": self.city,
                "zip": self.zip,
                "state_id": Partner.get_state_from_code(self.state, self.country),
                "country_id": Partner.get_country_from_code(self.country),
                "partner_latitude": self.partner_latitude or 0,
                "partner_longitude": self.partner_longitude or 0,
                "date_validation": fields.Date.today(),
                "validation_method": "avatax",
            }
            address.write(vals)
        return {"type": "ir.actions.act_window_close"}
