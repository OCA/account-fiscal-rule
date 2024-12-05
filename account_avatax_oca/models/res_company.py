import logging

from odoo import models

_LOGGER = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    def get_avatax_config_company(self):
        """Returns the AvaTax configuration for the Company"""
        if self:
            self.ensure_one()
            AvataxConfig = self.env["avalara.salestax"]
            res = AvataxConfig.search(
                [("company_id", "=", self.id), ("disable_tax_calculation", "=", False)]
            )
            if len(res) > 1:
                _LOGGER.warning(
                    self.env._("Company %s has too many Avatax configurations!"),
                    self.display_name,
                )
            if len(res) < 1:
                _LOGGER.warning(
                    self.env._("Company %s has no Avatax configuration."),
                    self.display_name,
                )
            return res and res[0]
