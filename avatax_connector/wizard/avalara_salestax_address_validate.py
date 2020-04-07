import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AvalaraSalestaxAddressValidate(models.TransientModel):
    """Address Validation using Avalara API"""
    _name = 'avalara.salestax.address.validate'
    _description = 'Address Validation using AvaTax'

    original_street = fields.Char('Original Street', readonly=True)
    original_street2 = fields.Char('Original Street2', readonly=True)
    original_city = fields.Char('Original City', readonly=True)
    original_zip = fields.Char('Original Zip', readonly=True)
    original_state = fields.Char('Original State', readonly=True)
    original_country = fields.Char('Original Country', readonly=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    zip = fields.Char('Zip')
    state = fields.Char('State')
    country = fields.Char('Country')
    partner_latitude = fields.Float('Latitude')
    partner_longitude = fields.Float('Longitude')

    @api.model
    def default_get(self, fields):
        """  Returns the default values for the fields. """
        res = super(AvalaraSalestaxAddressValidate, self).default_get(fields)

        context = dict(self._context or {})
        active_id = context.get('active_id')

        if active_id:
            address_obj = self.env['res.partner']
            address_brw = address_obj.browse(active_id)
            address_brw.write({
                'partner_latitude': 0,
                'partner_longitude': 0,
                'date_validation': False,
                'validation_method': '',
            })

            address = address_brw.read(
                ['street', 'street2', 'city', 'state_id', 'zip', 'country_id'])[0]
            address['state_id'] = address.get(
                'state_id') and address['state_id'][0]
            address['country_id'] = address.get(
                'country_id') and address['country_id'][0]
            # Get the valid result from the AvaTax Address Validation Service
            valid_address = address_obj._validate_address(address)
            if 'original_street' in fields:
                res.update({'original_street': address['street']})
            if 'original_street2' in fields:
                res.update({'original_street2': address['street2']})
            if 'original_city' in fields:
                res.update({'original_city': address['city']})
            if 'original_state' in fields:
                res.update(
                    {'original_state': address_obj.get_state_code(address['state_id'])})
            if 'original_zip' in fields:
                res.update({'original_zip': address['zip']})
            if 'original_country' in fields:
                res.update(
                    {'original_country': address_obj.get_country_code(address['country_id'])})
            if 'street' in fields:
                res.update({'street': str(valid_address.Line1 or '')})
            if 'street2' in fields:
                res.update({'street2': str(valid_address.Line2 or '')})
            if 'city' in fields:
                res.update({'city': str(valid_address.City or '')})
            if 'state' in fields:
                res.update({'state': str(valid_address.Region or '')})
            if 'zip' in fields:
                res.update({'zip': str(valid_address.PostalCode or '')})
            if 'country' in fields:
                res.update({'country': str(valid_address.Country or '')})
            if 'partner_latitude' in fields:
                res.update({'partner_latitude': valid_address.Latitude or 0})
            if 'partner_longitude' in fields:
                res.update({'partner_longitude': valid_address.Longitude or 0})
        return res

    def accept_valid_address(self):
        """ Updates the existing address with the valid address returned by the service. """
        valid_address = self.read()[0]
        context = dict(self._context or {})
        active_id = context.get('active_id')
        if active_id:
            address_obj = self.env['res.partner']
            address_brw = address_obj.browse(active_id)
            address_result = {
                'street': valid_address['street'],
                'street2': valid_address['street2'],
                'city': valid_address['city'],
                'state_id': address_obj.get_state_id(valid_address['state'], valid_address['country']),
                'zip': valid_address['zip'],
                'country_id': address_obj.get_country_id(valid_address['country']),
                'partner_latitude': valid_address['partner_latitude'] or 0,
                'partner_longitude': valid_address['partner_longitude'] or 0,
                'date_validation': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'validation_method': 'avatax'
            }
            address_brw.write(address_result)
        return {'type': 'ir.actions.act_window_close'}
