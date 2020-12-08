# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    customer_vat_partner_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_customer_vat_partner_id",
        readonly=False,
        store=True,
    )

    @api.depends("partner_shipping_id")
    def _compute_customer_vat_partner_id(self):
        partner_m = self.env["res.partner"]
        for rec in self:
            if not rec.partner_shipping_id or rec.type not in (
                "out_invoice",
                "out_refund",
            ):
                rec.customer_vat_partner_id = False
                continue
            rec.customer_vat_partner_id = partner_m._get_tax_administration_for_country(
                rec.partner_shipping_id.country_id
            )
