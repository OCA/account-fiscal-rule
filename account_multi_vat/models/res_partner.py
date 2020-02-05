# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_tax_administration = fields.Boolean(
        string="Tax administration", default=False, copy=False
    )
    has_vat = fields.Boolean(compute="_compute_has_vat", readonly=True, store=False)

    def _compute_has_vat(self):
        partner_id_vat_category = self.env.ref(
            "account_multi_vat.partner_id_category_vat", raise_if_not_found=False
        )
        for rec in self:
            rec.has_vat = (
                partner_id_vat_category
                and rec.vat
                or any(
                    n.category_id == partner_id_vat_category for n in self.id_numbers
                )
            )

    @api.model
    def _get_tax_administration_for_country(self, country):
        return self.sudo().search(
            [("is_tax_administration", "=", True), ("country_id", "=", country.id)],
            limit=1,
        )

    def _get_vat_number_for_administration(self, administration_partner=None):
        self.ensure_one()
        if not administration_partner:
            administration_partner = self.env.company.partner_id
        partner_id_vat_category = self.env.ref(
            "account_multi_vat.partner_id_category_vat", raise_if_not_found=False
        )
        id_number = self.id_numbers.filtered(
            lambda n: n.category_id == partner_id_vat_category
            and n.partner_issued_id == administration_partner
        )
        res = id_number and id_number.name
        return res or self.vat

    def _get_vat_number_for_country(self, country):
        self.ensure_one()
        tax_administration = self.env[
            "res.partner"
        ]._get_tax_administration_for_country(country)
        return self._get_vat_number_for_administration(tax_administration)

    @api.constrains("is_tax_administration")
    def _check_is_tax_administration(self):
        if any(rec.is_tax_administration and not rec.country_id for rec in self):
            raise ValidationError(
                _(u"The country is mandatory for tax administrations.")
            )
        country_model = self.env["res.country"]
        partner_model = self.env["res.partner"]
        read_group_res = partner_model.sudo().read_group(
            domain=[
                ("country_id", "!=", False),
                ("country_id", "in", self.mapped("country_id").ids),
                ("is_tax_administration", "=", True),
            ],
            fields=["country_id"],
            groupby=["country_id"],
        )
        for read_group_dic in read_group_res:
            if read_group_dic.get("country_id_count", 0) > 1:
                country = country_model.sudo().browse(read_group_dic["country_id"][0])
                raise ValidationError(
                    _("There's already a tax administration for {country_name}").format(
                        country_name=country.name
                    )
                )
