# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("partner_id", "partner_shipping_id", "company_id")
    def _compute_fiscal_position_id(self):
        """Override to pass the seller to _get_fiscal_position().

        The triplet varies according to the move type:

        Outgoing invoices (out_invoice, out_refund) — company is seller:
        - seller   = company_id.partner_id
        - buyer    = partner_id (customer)
        - delivery = partner_shipping_id (already resolved by Odoo, falls back
                     to the customer's delivery address)

        Incoming invoices (in_invoice, in_refund) — company is buyer:
        - seller   = partner_id (supplier)
        - buyer    = company_id.partner_id
        - delivery = partner_shipping_id, which in a dropship scenario holds
                     the end customer's address (populated by procurement rules)
                     and in a standard purchase holds the warehouse address.

        In both cases passing partner_shipping_id as delivery is correct:
        - Standard purchase: warehouse in same country as company → neutral
        - Dropship purchase: end customer address → our algorithm ignores it
          if the supplier is in EU and the buyer (company) is outside EU,
          correctly yielding an export fiscal position.

        ``seller`` and ``is_service`` are passed via context keys
        ``fp_eu_seller`` and ``fp_eu_is_service`` to avoid breaking the
        ``_get_fiscal_position()`` signature used by other modules (e.g.
        account_avatax_oca) that may also override this method without
        knowing these parameters.
        """
        for move in self:
            if not move.partner_id:
                move.fiscal_position_id = False
                continue

            # Resolve delivery address, mirroring Odoo's native logic.
            delivery = move.partner_shipping_id or self.env["res.partner"].browse(
                move.partner_id.address_get(["delivery"])["delivery"]
            )

            if move.is_sale_document():
                seller = move.company_id.partner_id
                partner = move.partner_id
            elif move.is_purchase_document():
                seller = move.partner_id
                partner = move.company_id.partner_id
            else:
                # Other move types (entries, etc.): fall back to Odoo default.
                move.fiscal_position_id = (
                    self.env["account.fiscal.position"]
                    .with_company(move.company_id)
                    ._get_fiscal_position(move.partner_id, delivery=delivery)
                )
                continue

            move.fiscal_position_id = (
                self.env["account.fiscal.position"]
                .with_company(move.company_id)
                .with_context(fp_eu_seller=seller)
                ._get_fiscal_position(partner, delivery=delivery or None)
            )
