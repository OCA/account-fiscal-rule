Once installed, fiscal position resolution on all invoices and credit notes
automatically uses the full vendor + buyer + delivery address triplet.

No manual action is required. The correction applies to all moves created or
recomputed after installation, including those generated automatically by
``account_invoice_inter_company``.

For the correction to also apply upstream at order level, install the companion
modules:

- ``sale_fiscal_position_eu_rule`` — for sale orders
- ``purchase_fiscal_position_eu_rule`` — for purchase orders
