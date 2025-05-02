from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_id", "partner_shipping_id")
    def _onchange_partner_shipping_id(self):
        for move in self:
            move.tax_on_shipping_address = bool(move.partner_shipping_id)

    def add_retail_delivery_fee_product(self):
        avatax_config = self.company_id.get_avatax_config_company()
        if avatax_config:
            retail_delivery_fees = avatax_config.retail_delivery_fee_ids.filtered(
                lambda r: r.country_id.code == self.tax_address_id.country_id.code
                and r.state_id.code == self.tax_address_id.state_id.code
            )
            retail_delivery_fee = next(
                (
                    rdf
                    for rdf in retail_delivery_fees
                    if rdf.enabled and rdf.should_apply_to(self)
                ),
                None,
            )

            if retail_delivery_fee:
                origin_sales = self.line_ids.sale_line_ids.order_id
                if not origin_sales:
                    return super().add_retail_delivery_fee_product()
                if any(
                    sale.has_existing_rdf_invoice(self, retail_delivery_fee)
                    for sale in origin_sales
                ):
                    return
