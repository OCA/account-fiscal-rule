- Support for sellers established outside the EU (UK, US, CN). A companion
  module ``account_fiscal_position_uk_rule`` is planned to cover post-Brexit
  UK VAT rules.
- Support for the €10,000 B2C threshold (Article 59c of Directive 2006/112/EC)
  below which the place of supply remains in the seller's Member State.
- Automatic ``is_service`` detection for mixed goods/services orders.
- Support for electronically supplied services (OSS mandatory above threshold).
- Interaction with ``foreign_vat`` fiscal positions: when the selling company
  is locally registered for VAT in a destination EU country (``foreign_vat``
  set on an existing fiscal position for that country), ``l10n_eu_oss`` skips
  OSS for that country and the local-registration FP applies instead.  This
  module does not detect this situation and will resolve the FP using the
  standard EU rules regardless.  Correct handling requires inspecting
  ``account.fiscal.position`` records with ``foreign_vat != False`` before
  delegating to ``super()``.

Known limitations of ``base.europe``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

EU membership is currently detected via the ``base.europe`` country group
(``res.country.group`` xmlid ``base.europe``).  This group closely matches the
27 Member States but does not perfectly reflect the VAT territory defined by
Directive 2006/112/EC, arts. 6–7.  The following cases are **not handled**:

EU territories **excluded** from the VAT directive scope (treated as EU by
this module, should be treated as export):

- French overseas territories: Guadeloupe, Martinique, Réunion, Guyane,
  Mayotte (DOM — these are separate countries in Odoo, not part of FR)
- Canary Islands, Ceuta and Melilla (ES)
- Åland Islands (FI)
- Mount Athos / Ágion Óros (GR)
- Livigno and Campione d'Italia (IT)
- Helgoland and Büsingen am Hochrhein (DE)

Non-EU territories **included** in the VAT directive scope (treated as
non-EU by this module, should be treated as domestic/intra-Community):

- Monaco (MC) — follows French VAT rules
- Sovereign Base Areas of Akrotiri and Dhekelia (GB territory on Cyprus)
