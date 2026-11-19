# Copyright 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models

from odoo.addons.account.models.product import ACCOUNT_DOMAIN


class ProductTemplate(models.Model):
    _inherit = "product.template"

    property_account_refund_in_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        ondelete="restrict",
        domain=ACCOUNT_DOMAIN,
        string="Refund In Account",
        help="Keep this field empty to use the default value from the product "
        "category.",
    )
    property_account_refund_out_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        ondelete="restrict",
        domain=ACCOUNT_DOMAIN,
        string="Refund Out Account",
        help="Keep this field empty to use the default value from the product "
        "category.",
    )
