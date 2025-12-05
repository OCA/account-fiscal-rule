# Copyright 2025 Pierre Verkest <pierre@verkest.fr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class AccountTaxProductAmount(models.Model):
    _name = "account.tax.product.amount"
    _description = "Account Tax Product Amounts (ie: usefull to manage ecotax)"
    _check_company_auto = True
    _order = "company_id, product_id, tax_id"

    product_id = fields.Many2one(
        "product.product",
        string="Product Variant",
        required=True,
        ondelete="cascade",
        check_company=True,
    )
    tax_id = fields.Many2one(
        "account.tax",
        string="Tax",
        required=True,
        check_company=True,
        domain=(
            "[('use_product_amount', '=', True), "
            " ('amount_type', '=', 'fixed'), "
            " ('company_id', 'in', [False, company_id])]"
        ),
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.tax_id.company_id or self.env.company,
    )
    type_tax_use = fields.Selection(
        related="tax_id.type_tax_use",
    )
    amount = fields.Float(
        required=True,
        digits=(16, 4),
        default=0.0,
    )

    _sql_constraints = [
        (
            "product_tax_unique",
            "UNIQUE(product_id, tax_id)",
            "The tax amount must be unique per product variant and tax.",
        )
    ]
