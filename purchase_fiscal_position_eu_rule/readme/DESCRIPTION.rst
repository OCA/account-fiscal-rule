This module is a companion to ``account_fiscal_position_eu_rule``. It patches
the fiscal position resolution on purchase orders so that the full vendor +
buyer + delivery address triplet is taken into account.

In a purchase order, the triplet is inverted compared to a sale order:

- **Seller**: the supplier (``partner_id``)
- **Buyer**: the purchasing company (``company_id.partner_id``)
- **Delivery**: the dropship address (``dest_address_id``) if set, otherwise
  the warehouse address (``picking_type_id.warehouse_id.partner_id``)

Without this module, Odoo's native ``onchange_partner_id()`` on
``purchase.order`` only passes the supplier to ``_get_fiscal_position()``,
ignoring both the buyer's country and the delivery address. This leads to
incorrect VAT treatment in dropship scenarios.

See ``account_fiscal_position_eu_rule`` for the full list of corrected cases
and the underlying EU VAT rules.
