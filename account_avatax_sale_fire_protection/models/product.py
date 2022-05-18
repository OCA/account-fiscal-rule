# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Product(models.Model):
    _inherit = "product.template"

    tax_swapping_product_id = fields.Many2one(
        "product.product", string="Conditional Taxable Product"
    )
