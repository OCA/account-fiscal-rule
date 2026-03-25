Once installed, fiscal position resolution on sale orders automatically uses
the full vendor + buyer + delivery address triplet.

No manual action is required. The correction applies to all sale orders created
or recomputed after installation.

For the correction to also apply to purchase orders and invoices created without
a sale order, install the companion modules:

- ``purchase_fiscal_position_eu_rule`` — for purchase orders
- ``account_move_fiscal_position_eu_rule`` — for standalone invoices
