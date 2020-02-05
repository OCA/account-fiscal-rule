# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    customer_vat = fields.Char(
        string="Customer VAT",
        compute="_compute_customer_vat",
        readonly=True,
        store=True,
    )
    customer_vat_partner_id = fields.Many2one(
        string="Customer tax administration",
        comodel_name="res.partner",
        ondelete="restrict",
        domain=[("is_tax_administration", "=", True)],
    )

    @api.depends("partner_id", "customer_vat_partner_id")
    def _compute_customer_vat(self):
        for rec in self:
            if not rec.partner_id or rec.type not in ("out_invoice", "out_refund"):
                rec.customer_vat = False
                continue
            rec.customer_vat = rec.partner_id._get_vat_number_for_administration(
                rec.customer_vat_partner_id
            )
