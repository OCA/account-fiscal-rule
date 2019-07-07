from odoo import api, fields, models, _
#from odoo.exceptions import ValidationError
#from .avatax_api import TaxCloudRequest


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    avatax_account_number = fields.Char(
        config_parameter='avatax_connector.avatax_account_number')
    avatax_license_key = fields.Char(
        config_parameter='avatax_connector.avatax_license_key')
    avatax_api_environment = fields.Selection(
        [('sandbox', 'Sandbox'), ('prod', 'production')],
        config_parameter='avatax_connector.avatax_api_environment')

    @api.multi
    def avatax_test(self):
        Category = self.env['product.tic.category']
        request = TaxCloudRequest(self.taxcloud_api_id, self.taxcloud_api_key)
        res = request.get_tic_category()

        if res.get('error_message'):
            raise ValidationError(_('Unable to retrieve taxes from TaxCloud: ')+'\n'+res['error_message']+'\n\n'+_('The configuration of TaxCloud is in the Accounting app, Settings menu.'))

        for category in res['data']:
            if not Category.search([('code', '=', category['TICID'])], limit=1):
                Category.create({'code': category['TICID'], 'description': category['Description']})
        if not self.env.user.company_id.tic_category_id:
            self.env.user.company_id.tic_category_id = Category.search([('code', '=', 0)], limit=1)
        return True
