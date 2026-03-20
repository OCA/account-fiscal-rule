This module is a companion to ``account_fiscal_position_eu_rule``. It patches
the fiscal position resolution on account moves (invoices and credit notes) so
that the full vendor + buyer + delivery address triplet is taken into account.

The triplet depends on the move type:

**Outgoing invoices and credit notes** (``out_invoice``, ``out_refund``):

- **Seller**: the current company (``company_id.partner_id``)
- **Buyer**: the customer (``partner_id``)
- **Delivery**: ``partner_shipping_id`` (already resolved by Odoo)

**Incoming invoices and credit notes** (``in_invoice``, ``in_refund``):

- **Seller**: the supplier (``partner_id``)
- **Buyer**: the current company (``company_id.partner_id``)
- **Delivery**: ``partner_shipping_id``, which holds the end customer address
  in dropship scenarios (populated by procurement rules) or the warehouse
  address in standard purchase flows.

Other move types (journal entries, etc.) are not affected and fall back to
Odoo's native resolution.

This module is particularly useful for invoices created directly without a sale
or purchase order (e.g. via ``account_invoice_inter_company``), where the
fiscal position is computed solely from the invoice fields.

See ``account_fiscal_position_eu_rule`` for the full list of corrected cases
and the underlying EU VAT rules.
