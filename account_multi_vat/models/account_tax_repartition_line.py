# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"

    country_id = fields.Many2one(
        comodel_name="res.country", related="tax_id.country_id"
    )
