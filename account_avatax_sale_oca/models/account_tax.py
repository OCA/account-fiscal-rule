from odoo import models


class AccountTax(models.Model):
    _inherit = "account.tax"

    def compute_all(
        self,
        price_unit,
        currency=None,
        quantity=1.0,
        product=None,
        partner=None,
        is_refund=False,
        handle_price_include=True,
        include_caba_tags=False,
    ):
        res = super().compute_all(
            price_unit,
            currency,
            quantity,
            product,
            partner,
            is_refund,
            handle_price_include,
            include_caba_tags=False,
        )
        for_avatax_object = self.env.context.get("for_avatax_object")
        if for_avatax_object:
            # Find the Avatax amount in the document Lines
            # Looks up the line for the current product, price_unit, and quantity
            # Note that the price_unit used must consider discount
            avatax_ids = self.env["account.tax"].search([("is_avatax", "=", True)]).ids
            for tax_data in [x for x in res["taxes"] if x["id"] in avatax_ids]:
                line = for_avatax_object.order_line.filtered(
                    lambda x: tax_data["id"] in x.tax_id.ids
                    and x.product_id == product
                    and x.product_uom_qty == quantity
                    and x.price_unit == price_unit
                )[:1]
                if line.tax_amt:  # Avatax Amount
                    tax_data["amount"] = line.tax_amt
                    res["total_included"] = res["total_excluded"] + line.tax_amt
        return res
