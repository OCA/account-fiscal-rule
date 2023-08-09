# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SignOcaRequest(models.Model):
    _inherit = "sign.oca.request"

    is_exemption = fields.Boolean(related="template_id.is_exemption")
    is_exemption_synchronized = fields.Boolean(
        string="Exemption synchronized with AvaTax?",
        readonly=True,
        copy=False
    )
    exemption_ids = fields.One2many(
        comodel_name="res.partner.exemption",
        inverse_name="sign_oca_request_id",
        string="Exemptions"
    )

    def _get_partner_id(self):
        role_customer = self.env.ref("sign_oca.sign_role_customer")
        customer_signers = self.signer_ids.filtered(lambda x: x.role_id == role_customer).partner_id
        return customer_signers[0] if customer_signers else None

    def _prepare_exemption_data(self):
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("exemption_export", "=", True)], limit=1)
        )
        use_commercial_entity = avalara_salestax.use_commercial_entity
        partner_id = self._get_partner_id()

        data = {
            "partner_id": partner_id.commercial_partner_id.id
            if use_commercial_entity
            else partner_id.id,
            "exemption_type": self.template_id.exemption_type.id,
            "sign_request_id": self.id,
        }
        exemption_number_field_id = self.template_id.item_ids.mapped("field_id").filtered(lambda x: x.is_exemption_number).ids
        if exemption_number_field_id:
            for item_id in self.signatory_data:
                item = self.signatory_data[item_id]
                if item["field_id"] == exemption_number_field_id[0]:
                    data["exemption_number"] = item["value"]
                    break
        return data

    def _check_signed(self):
        res = super()._check_signed()
        if self.state == "signed":
            if self.is_exemption:
                exemption_data = self._prepare_exemption_data()
                exemption = self.env["res.partner.exemption"].create(exemption_data)
                exemption.onchange_exemption_type()
                exemption.onchange_effective_date()
                exemption.onchange_state_ids()
                if exemption.exemption_number:
                    exemption.exemption_line_ids.write(
                        {
                            "add_exemption_number": True,
                            "exemption_number": exemption.exemption_number
                        }
                    )
        return res

    def open_exemptions(self):
        self.ensure_one()
        return {
            "name": "Exemptions",
            "type": "ir.actions.act_window",
            "res_model": "res.partner.exemption",
            "view_mode": "tree,form",
            "domain": [("sign_request_id", "=", self.id)],
        }
