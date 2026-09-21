# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    vat_partner_id = fields.Many2one(
        string="Tax administration",
        comodel_name="res.partner",
        ondelete="restrict",
        domain=[("is_tax_administration", "=", True)],
    )
