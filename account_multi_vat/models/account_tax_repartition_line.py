# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.osv import expression


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"

    tax_id = fields.Many2one(comodel_name="account.tax", search="_search_tax_id")
    country_id = fields.Many2one(
        comodel_name="res.country", related="tax_id.country_id"
    )

    def _search_tax_id(self, operator, value):
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = [
                ("invoice_tax_id", operator, value),
                ("refund_tax_id", operator, value),
            ]
        else:
            domain = [
                "|",
                ("invoice_tax_id", operator, value),
                ("refund_tax_id", operator, value),
            ]
        return domain
