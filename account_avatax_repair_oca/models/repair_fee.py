from odoo import api, fields, models


class RepairFee(models.Model):
    _inherit = "repair.fee"

    tax_amt_avatax = fields.Monetary(string="AvaTax")

    @api.depends("tax_amt_avatax")
    def _compute_price_total(self):
        res = super()._compute_price_total()
        for fee in self:
            fee.price_total = fee.price_subtotal + fee.tax_amt_avatax
        return res

    def _avatax_prepare_line(self, sign=1, doc_type=None):
        """
        Prepare a line to use for Avatax computation.
        Returns a dict
        """
        line = self
        res = {}
        # Add UPC to product item code
        avatax_config = line.company_id.get_avatax_config_company()
        product = line.product_id
        if product.barcode and avatax_config.upc_enable:
            item_code = "UPC:%d" % product.barcode
        else:
            item_code = product.default_code or ("ID:%d" % product.id)
        tax_code = line.product_id.applicable_tax_code_id.name
        amount = sign * line.price_unit * line.product_uom_qty
        # Calculate discount amount
        discount_amount = 0.0
        is_discounted = False
        res = {
            "qty": line.product_uom_qty,
            "itemcode": item_code,
            "description": line.name,
            "discounted": is_discounted,
            "discount": discount_amount,
            "amount": amount,
            "tax_code": tax_code,
            "id": line,
            "tax_id": line.tax_id,
        }
        return res

    @api.onchange("product_uom_qty", "price_unit", "tax_id")
    def onchange_reset_avatax_amount(self):
        """
        When changing quantities or prices, reset the Avatax computed amount.
        The Odoo computed tax amount will then be shown, as a reference.
        The Avatax amount will be recomputed upon document validation.
        """
        for line in self:
            line.tax_amt_avatax = 0
            line.repair_id.amount_tax_avatax = 0

    @api.depends("product_uom_qty", "price_unit", "tax_id", "tax_amt_avatax")
    def _compute_amount(self):
        """
        If we have a Avatax computed amount, use it instead of the Odoo computed one
        """
        super()._compute_amount()
        for line in self:
            if line.tax_amt_avatax:  # Has Avatax computed amount
                vals = {
                    "price_tax": line.tax_amt_avatax,
                    "price_total": line.price_subtotal + line.tax_amt_avatax,
                }
                line.update(vals)
        return
