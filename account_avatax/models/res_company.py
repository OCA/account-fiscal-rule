import logging
from ast import literal_eval

from odoo import _, api, fields, models

_LOGGER = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    def get_avatax_config_company(self):
        """ Returns the AvaTax configuration for the Company """
        if self:
            self.ensure_one()
            AvataxConfig = self.env["avalara.salestax"]
            res = AvataxConfig.search(
                [("company_id", "=", self.id), ("disable_tax_calculation", "=", False)]
            )
            if len(res) > 1:
                _LOGGER.warn(
                    _("Company %s has too many Avatax configurations!"),
                    self.display_name,
                )
            if len(res) < 1:
                _LOGGER.warn(
                    _("Company %s has no Avatax configuration."), self.display_name
                )
            return res and res[0]


class Settings(models.TransientModel):
    _inherit = "res.config.settings"

    avatax_api_call_notification_ids = fields.Many2many(
        "res.users",
        readonly=False,
    )
    call_counter_limit = fields.Integer(
        string="Call Counter Limit",
        config_parameter="account_avatax.call_counter_limit",
        default=100,
    )

    @api.model
    def get_values(self):
        res = super(Settings, self).get_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        get_param = "account_avatax.avatax_api_call_notification_ids"
        calls = ICPSudo.get_param(get_param)
        res.update(
            avatax_api_call_notification_ids=[(6, 0, literal_eval(calls))]
            if calls
            else False,
        )
        return res

    def set_values(self):
        res = super(Settings, self).set_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        set_param = "account_avatax.avatax_api_call_notification_ids"
        ICPSudo.set_param(set_param, self.avatax_api_call_notification_ids.ids)
        return res
