# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AvalaraSalestax(models.Model):
    _inherit = "avalara.salestax"

    def link_certificates_to_customer(self, exemption_line):
        res = super().link_certificates_to_customer(exemption_line)
        if all(
            exemption_line.exemption_id.exemption_line_ids.mapped("linked_to_customer")
        ):
            if exemption_line.exemption_id.sign_oca_request_id:
                exemption_line.exemption_id.sign_oca_request_id.write(
                    {
                        "is_exemption_synchronized": True,
                    }
                )
        return res
