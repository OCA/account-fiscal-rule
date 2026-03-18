No specific configuration is required for this module. It overrides
``_get_fiscal_position()`` transparently and relies on the fiscal positions
already configured in your Odoo instance.

For correct results, ensure the following:

- Each EU member state has a fiscal position configured for intra-Community
  B2B supplies (0% VAT + reverse charge mapping).
- An export fiscal position (0% VAT) is configured for buyers outside the EU.
- OSS fiscal positions are configured per destination country for B2C supplies.
- Buyer partner records include their VAT number when applicable.

Optional OCA modules improve B2B/B2C detection accuracy:

- ``base_vat_optional_vies`` (OCA/account-financial-tools): when installed
  and VIES is activated on the company (``vat_check_vies=True``), the result
  of VIES validation is used as the authoritative B2B/B2C signal.
- ``account_fiscal_position_partner_type`` (OCA/account-fiscal-rule): allows
  manual B2B/B2C qualification per partner via the ``fiscal_position_type``
  field. This is useful for partners whose VAT status cannot be determined
  from their VAT number alone (e.g. entities with a national tax identifier
  acting as B2C, or taxable persons not registered in VIES).
