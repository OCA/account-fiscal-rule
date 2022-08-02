from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("property_exemption_country_wide")
    def _onchange_property_exemption_contry_wide(self):
        if self.property_exemption_country_wide:
            message = (
                _(
                    "Enabling the exemption status for all states"
                    " may have tax compliance risks,"
                    " and should be carefully considered.\n\n"
                    " Please ensure that your tax advisor was consulted and the"
                    " necessary tax exemption documentation was obtained"
                    " for every state this Partner may have transactions."
                ),
            )
            return {"warning": {"title": _("Tax Compliance Risk"), "message": message}}

    property_exemption_country_wide = fields.Boolean(
        "Exemption Applies Country Wide",
        help="When enabled, the delivery address State is irrelevant"
        " when looking up the exemption status, meaning that the exemption"
        " is considered applicable for all states",
    )
