from odoo import fields, models


class RetailGroupState(models.Model):
    _name = "retail.group"
    _description = "Retail Delivery Fee"

    country_id = fields.Many2one(
        "res.country",
        required=True,
    )
    state_id = fields.Many2one(
        "res.country.state",
        required=True,
    )
    amount = fields.Float()
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
    )
    tax_ids = fields.Many2many(
        "account.tax",
        string="Taxes",
        domain=[("amount_type", "=", "fixed")],
        required=True,
    )
