# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields, models


class ResPartnerExemption(models.Model):
    _inherit = "res.partner.exemption"

    sign_oca_request_id = fields.Many2one("sign.oca.request")

    def write(self, vals):
        if vals.get("state") == "cancel":
            for record in self:
                record.sign_oca_request_id.cancel()
        return super().write(vals)

    def _rebuild_state_ids(self):
        self.business_type = self.exemption_type.business_type.id
        if self.exemption_type.group_of_state and not self.group_of_state:
            self.group_of_state = self.exemption_type.group_of_state.id
        if self.exemption_type or self.group_of_state:
            state_ids = []
            if self.exemption_type.group_of_state.state_ids:
                state_ids += self.exemption_type.group_of_state.state_ids.ids
            if self.exemption_type.state_ids:
                state_ids += self.exemption_type.state_ids.ids
            if self.group_of_state.state_ids:
                state_ids += self.group_of_state.state_ids.ids
            self.state_ids = [(6, 0, list(set(state_ids)))]

    def _rebuild_expiry_date(self):
        if self.exemption_type.exemption_validity_duration and self.effective_date:
            self.expiry_date = self.effective_date + timedelta(
                days=self.exemption_type.exemption_validity_duration
            )

    def _rebuild_exemption_lines(self):
        self.ensure_one()
        if not any(self.exemption_line_ids.mapped("avatax_id")) and not any(
            self.exemption_line_ids.mapped("add_exemption_number")
        ):
            self.exemption_line_ids.unlink()

        existing_state_ids = self.exemption_line_ids.mapped("state_id").ids
        for state_id in self.state_ids.ids:
            if state_id not in existing_state_ids:
                self.env["res.partner.exemption.line"].create(
                    {
                        "partner_id": self.partner_id.id,
                        "exemption_id": self.id,
                        "state_id": state_id,
                        "avatax_status": True,
                    }
                )
