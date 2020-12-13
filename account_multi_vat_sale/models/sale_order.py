# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
        compute="_compute_customer_vat_partner_id",
        readonly=False,
        store=True,
    )

    @api.depends("partner_id", "customer_vat_partner_id")
    def _compute_customer_vat(self):
        for rec in self:
            if not rec.partner_id:
                rec.customer_vat = False
                continue
            rec.customer_vat = rec.partner_id._get_vat_number_for_administration(
                rec.customer_vat_partner_id
            )

    @api.depends("partner_shipping_id")
    def _compute_customer_vat_partner_id(self):
        partner_m = self.env["res.partner"]
        for rec in self:
            if not rec.partner_shipping_id:
                rec.customer_vat_partner_id = False
                continue
            rec.customer_vat_partner_id = partner_m._get_tax_administration_for_country(
                rec.partner_shipping_id.country_id
            )
