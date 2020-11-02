# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartnerIdCategory(models.Model):
    _inherit = "res.partner.id_category"

    @api.model
    def _is_vat_code_valid(self, id_numbers):
        res_partner_model = self.env["res.partner"]
        for id_number in id_numbers:
            vat_code = id_number.name
            vat_country, vat_number = res_partner_model._split_vat(vat_code)
            return res_partner_model.vies_vat_check(vat_country, vat_number)
