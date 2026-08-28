# Copyright 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models

from odoo.addons.account.models.product import ACCOUNT_DOMAIN


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_account_refund_in_categ_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        domain=ACCOUNT_DOMAIN,
        string="Refund In Account",
        help="Account used for vendor credit notes of products in this category. "
        "Can be overridden per product. Leave empty to use the product's default "
        "expense account.",
        tracking=True,
        ondelete="restrict",
    )
    property_account_refund_out_categ_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        domain=ACCOUNT_DOMAIN,
        string="Refund Out Account",
        help="Account used for customer credit notes of products in this category. "
        "Can be overridden per product. Leave empty to use the product's default "
        "income account.",
        tracking=True,
        ondelete="restrict",
    )
