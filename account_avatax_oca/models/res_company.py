import logging

from odoo import _, fields, models

_LOGGER = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    allow_avatax_configuration = fields.Boolean(
        string="Active Avatax for this company",
        default=True,
        readonly=False,
    )

    def get_avatax_config_company(self):
        """Returns the AvaTax configuration for the Company"""
        if self:
            self.ensure_one()
            AvataxConfig = self.env["avalara.salestax"]
            if self.allow_avatax_configuration:
                res = AvataxConfig.search(
                    [
                        ("company_id", "=", self.id),
                        ("disable_tax_calculation", "=", False),
                    ]
                )
                if len(res) > 1:
                    _LOGGER.warning(
                        _("Company %s has too many Avatax configurations!"),
                        self.display_name,
                    )
                if len(res) < 1:
                    _LOGGER.warning(
                        _("Company %s has no Avatax configuration."), self.display_name
                    )
                return res and res[0]
            return AvataxConfig
