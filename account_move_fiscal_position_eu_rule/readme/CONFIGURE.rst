No specific configuration is required. Install this module alongside
``account_fiscal_position_eu_rule`` and ensure your fiscal positions are
correctly configured as described in that module's documentation.

For inter-company invoice flows using ``account_invoice_inter_company``, ensure
that ``partner_shipping_id`` is populated on the source invoice when a dropship
delivery address is involved. This is typically handled automatically by the
sale or purchase order that originated the invoice.
