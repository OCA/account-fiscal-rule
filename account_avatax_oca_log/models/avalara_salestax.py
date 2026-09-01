# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class AvalaraSalestax(models.Model):
    _inherit = "avalara.salestax"

    def void_transaction(self, doc_code, doc_type):
        result = super().void_transaction(doc_code, doc_type)
        if not self.disable_tax_reporting:
            self.env["avatax.log"].sudo().create(
                {
                    "avatax_request": result.get("id"),
                    "avatax_response": result,
                    "avatax_type": "cancel",
                }
            )
        return result
