# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_shipping_id", "partner_id", "company_id")
    def _compute_fiscal_position_id(self):
        """Override to pass the seller to _get_fiscal_position().

        Odoo's native implementation only passes the buyer (partner_id) and
        the delivery address (partner_shipping_id). This override adds the
        seller (company partner) so that EU VAT rules can be correctly applied
        when the buyer is outside the EU but the delivery address is within it
        (e.g. dropship from FR to a UK buyer delivering to an Irish customer).

        The native cache is intentionally not reproduced here to avoid key
        collision risks when seller is taken into account.
        """
        for order in self:
            if not order.partner_id:
                order.fiscal_position_id = False
                continue
            order.fiscal_position_id = (
                self.env["account.fiscal.position"]
                .with_company(order.company_id)
                .with_context(fp_eu_seller=order.company_id.partner_id)
                ._get_fiscal_position(
                    order.partner_id,
                    delivery=order.partner_shipping_id or None,
                )
            )

    def _prepare_invoice(self):
        """Override to pass the seller to _get_fiscal_position() in the
        fallback call that occurs when fiscal_position_id is not set.

        In practice this fallback is rarely triggered since
        _compute_fiscal_position_id() already runs at SO confirmation, but
        patching it ensures full consistency if the FP is ever empty at
        invoicing time.
        """
        vals = super()._prepare_invoice()
        if not self.fiscal_position_id:
            vals["fiscal_position_id"] = (
                self.env["account.fiscal.position"]
                .with_company(self.company_id)
                .with_context(fp_eu_seller=self.company_id.partner_id)
                ._get_fiscal_position(
                    self.partner_invoice_id, delivery=self.partner_shipping_id or None
                )
            ).id
        return vals
