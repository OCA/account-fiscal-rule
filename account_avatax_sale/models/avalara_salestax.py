from odoo import fields, models


class AvalaraSalestax(models.Model):
    _inherit = "avalara.salestax"

    use_partner_invoice_id = fields.Boolean(
        "Use Invoice partner's customer code in SO",
    )
    sale_calculate_tax = fields.Boolean(
        "Auto Calculate Tax on SO Save",
        help="Automatically triggers API to calculate tax If changes made on"
        "SO's warehouse_id, tax_on_shipping_address, "
        "SO line's price_unit, discount, product_uom_qty",
    )
