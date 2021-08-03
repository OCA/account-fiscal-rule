import logging

from odoo import _, fields, models

_LOGGER = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    avatax_api_call_notification = fields.Char(
        string="Avatax API Call Notification",
    )

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

    avatax_api_call_notification = fields.Char(
        readonly=False,
        related="company_id.avatax_api_call_notification",
    )
