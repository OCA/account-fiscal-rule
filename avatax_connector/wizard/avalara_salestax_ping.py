from odoo import api, fields, models
from odoo.addons.avatax_connector.models.avatax_rest_api import AvaTaxRESTService


class AvalaraSalestaxPing(models.TransientModel):
    _name = 'avalara.salestax.ping'
    _description = 'Ping Service'

    @api.model
    def default_get(self, fields):
        res = super(AvalaraSalestaxPing, self).default_get(fields)
        self.ping()
        return res

    name = fields.Char('Name')

    @api.model
    def ping(self):
        """ Call the AvaTax's Ping Service to test the connection. """
        context = dict(self._context or {})
        active_id = context.get('active_id')

        if active_id:
            avatax_config = self.env['avalara.salestax'].browse(active_id)
            avatax_restpoint = AvaTaxRESTService(
                avatax_config.account_number,
                avatax_config.license_key,
                avatax_config.service_url,
                avatax_config.request_timeout,
                avatax_config.logging)
            avatax_restpoint.ping()
            avatax_config.write({'date_expiration': '9998-12-31'})
        return True
