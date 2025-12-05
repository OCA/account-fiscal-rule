# Copyright 2025 Pierre Verkest <pierre@verkest.fr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    tax_amount_ids = fields.One2many(
        "account.tax.product.amount",
        "product_id",
        string="Tax fixed amounts",
        help="Define specific tax fixed amounts for this variant.",
    )
