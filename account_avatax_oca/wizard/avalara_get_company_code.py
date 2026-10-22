from odoo import fields, models
from odoo.exceptions import UserError

from ..models.avatax_rest_api import AvaTaxRESTService


class AvalaraSalestaxGetCompany(models.TransientModel):
    _name = "avalara.salestax.getcompany"
    _description = "Avatax Get Company Code"

    def _get_company_codes(self):
        active_id = self.env.context.get("active_id") or self.env.context.get(
            "active_id_view_ref"
        )
        config = self.env["avalara.salestax"].browse(active_id)
        if not config:
            config = self.env["avalara.salestax"].search([], limit=1)
        avatax_api = AvaTaxRESTService(config=config)
        response = avatax_api.client.query_companies()
        response_data = response.json()
        if response_data and response_data.get("error"):
            raise UserError(response_data.get("error", {}).get("message", "Error"))
        return [
            (x["companyCode"], "{} ({})".format(x["name"], x["companyCode"]))
            for x in response_data["value"]
        ]

    company_code = fields.Selection(
        selection=_get_company_codes,
        string="Select a Company",
    )

    def action_set_code(self):
        if self.company_code:
            active_id = self.env.context.get("active_id")
            config = self.env["avalara.salestax"].browse(active_id)
            config.company_code = self.company_code
        return True
