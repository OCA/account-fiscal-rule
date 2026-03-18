This module acts automatically. Once installed, ``_get_fiscal_position()`` uses
the seller's company country in addition to the buyer and delivery address to
resolve the correct fiscal position.

To benefit from the corrected resolution in sales orders, purchases orders and
invoices, install the corresponding companion modules:

- ``sale_fiscal_position_eu_rule`` — for sale orders
- ``purchase_fiscal_position_eu_rule`` — for purchase orders
- ``account_move_fiscal_position_eu_rule`` — for invoices created without a
  sale or purchase order

Each companion module patches the relevant onchange to pass the ``seller``
parameter to ``_get_fiscal_position()``.

For transactions involving services rather than physical goods, the caller is
responsible for passing ``is_service=True`` to ``_get_fiscal_position()`` so
that Article 44/45 rules are applied instead of the goods delivery rules.
