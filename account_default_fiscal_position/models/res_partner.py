# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)

        if partner.country_id and partner.vat:
            fiscal_position_line = self.env["fiscal.position.line"].search(
                [("country_id", "=", partner.country_id.id)]
            )
            if fiscal_position_line:
                fiscal_position = fiscal_position_line.fiscal_position_id
                partner.property_account_position_id = fiscal_position
        return partner
