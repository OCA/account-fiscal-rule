# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.account_avatax_oca.models.avatax_rest_api import AvaTaxRESTService


class AvaTaxRESTServiceExtended(AvaTaxRESTService):
    def _get_tax_post_process(self, data, result, doc_type):
        self.config.env["avatax.log"].sudo().create(
            {
                "avatax_request": data,
                "avatax_response": result,
                "avatax_type": "SalesOrder"
                if doc_type in ["SalesOrder", "ReturnOrder"]
                else "SalesInvoice",
            }
        )
        return True
