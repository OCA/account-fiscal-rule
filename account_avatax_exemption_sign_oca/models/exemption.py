# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartnerExemption(models.Model):
    _inherit = "res.partner.exemption"

    sign_oca_request_id = fields.Many2one("sign.oca.request")

    @api.depends("state")
    def _cancel_sign_request_id(self):
        for rec in self:
            if rec.state == "cancel":
                rec.sign_oca_request_id.cancel()
