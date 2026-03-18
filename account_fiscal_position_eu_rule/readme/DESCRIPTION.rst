This module enriches Odoo's fiscal position resolution by taking into account
the full triplet of addresses involved in a transaction: the seller, the buyer,
and the delivery address.

Odoo's native ``_get_fiscal_position()`` method only considers the buyer and
optionally the delivery address, which leads to incorrect VAT treatment in
several cross-border scenarios involving EU companies.

This module corrects the following cases for sellers established in the EU:

- **Buyer outside the EU** (e.g. UK, US): the delivery address is irrelevant.
  The transaction is an export and must be invoiced at 0% VAT regardless of
  where the goods are delivered.

- **B2B buyer in the EU** (valid VAT number): the transaction is an
  intra-Community supply (0% VAT + reverse charge) if goods are delivered to
  another Member State, or a domestic supply if delivered within the seller's
  country.

- **B2C buyer in the EU** (no valid VAT number): when goods are delivered to
  another Member State, the OSS regime applies and the VAT rate of the delivery
  country must be used. When goods are delivered within the seller's country,
  the domestic fiscal position applies.

- **Services (B2B)**: under Article 44 of Directive 2006/112/EC, the place of
  supply is the buyer's country regardless of where the service is performed.
  The delivery address is therefore irrelevant.

- **Services (B2C)**: under Article 45, the place of supply is the seller's
  country regardless of where the buyer is located — even for buyers outside
  the EU. The domestic fiscal position of the seller always applies.

This module requires no extra dependency beyond the ``base`` module.
EU membership is determined via the ``base.europe`` country group, which is
always present in Odoo. Note that ``base.europe`` is an approximation of the
VAT territory defined by Directive 2006/112/EC (arts. 6–7): a small number of
territories are misclassified (see *Roadmap* below).

B2B/B2C detection
~~~~~~~~~~~~~~~~~

The B2B/B2C qualification of a transaction is based exclusively on the
**buyer's** (preneur's) status — never on the delivery address. The delivery
address determines the place of supply (which OSS rate applies in B2C), but
never the B2B/B2C nature of the transaction.

Detection priority (highest to lowest):

1. **VIES validation** (``base_vat_optional_vies``, OCA): when VIES is
   activated on the company (``vat_check_vies=True``), ``vies_passed`` on
   the buyer's partner is authoritative. When VIES is disabled,
   ``vies_passed`` is always ``False`` and is ignored.

2. **Manual type** (``account_fiscal_position_partner_type``, OCA): the
   ``fiscal_position_type`` field on the buyer's partner record, set
   manually by the user. This covers cases where neither VAT presence nor
   VIES is sufficient (e.g. entities with a national tax number acting as
   B2C, or taxable persons not registered in VIES).

3. **VAT number presence**: fallback when neither of the above modules is
   installed or the fields are not set.

Compatibility with ``account_fiscal_position_partner_type``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``account_fiscal_position_partner_type`` overrides ``_get_fiscal_position()``
to filter fiscal positions by ``delivery.fiscal_position_type``. Because the
MRO order of these two modules is not guaranteed, this module takes an explicit
compatibility step for B2C cross-border goods supplies (the only case where
the conflict can occur): before calling ``super()``, it temporarily sets
``fiscal_position_type="b2c"`` on both the partner and the delivery address
records, and injects the same value into the context. The original values are
restored immediately after. This ensures that ``account_fiscal_position_partner_type``
always filters on B2C fiscal positions when our module has decided the buyer
is B2C, regardless of which module is higher in the MRO.
