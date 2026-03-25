No specific configuration is required. Install this module alongside
``account_fiscal_position_eu_rule`` and ensure your fiscal positions are
correctly configured as described in that module's documentation.

The ``purchase_stock`` module is supported but not required:

- When installed, the delivery address is resolved from ``dest_address_id``
  (dropship address) or ``picking_type_id.warehouse_id.partner_id``
  (warehouse address), whichever is set first.
- When absent (base ``purchase`` module only), no delivery address is passed
  to ``_get_fiscal_position()``. The fiscal position is then resolved solely
  from the supplier's country, which is correct for non-dropship flows.

For dropship flows, ensure that ``dest_address_id`` is correctly populated on
purchase orders by your procurement rules. Odoo's native dropship route does
this automatically.
