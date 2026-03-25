This module is a companion to ``account_fiscal_position_eu_rule``. It patches
the fiscal position resolution on sale orders so that the seller's company
address is taken into account alongside the buyer and delivery address.

Without this module, Odoo's native ``_compute_fiscal_position_id()`` on
``sale.order`` only considers the buyer (``partner_id``) and the delivery
address (``partner_shipping_id``). This leads to incorrect VAT treatment in
dropship scenarios where the buyer is outside the EU but the goods are
delivered to an EU address (e.g. a French company selling to a UK subsidiary
that drops ships to an Irish end customer).

This module fixes both the fiscal position computation on the sale order and
the fallback call in ``_prepare_invoice()``.

See ``account_fiscal_position_eu_rule`` for the full list of corrected cases
and the underlying EU VAT rules.
