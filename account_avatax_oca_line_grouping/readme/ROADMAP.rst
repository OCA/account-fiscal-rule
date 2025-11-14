The main goal of this addon is to support **single-sale / bulk / working-unit**
tax scenarios by grouping all document lines into a single line for AvaTax.

The current implementation provides a simple, company-wide switch:
when enabled, all Sales Orders and Customer Invoices for that company
are sent to AvaTax as a single aggregated line.

Possible future improvements
----------------------------

The following enhancements are candidates for future versions:

- **Per-fiscal-position control**

  Allow enabling line grouping per *Fiscal Position* instead of (or in
  addition to) a global company flag.  
  Example: only apply grouping when a dedicated “Single Sale / Bulk”
  fiscal position is used.

- **Per-document or per-partner control**

  Add an option on Sales Orders / Invoices and/or on partners to override
  the company setting, so that grouping can be enabled/disabled on a
  case-by-case basis.

- **Grouping strategies**

  Support different grouping strategies, such as:

  - Group only lines that share the same product tax code.
  - Group only lines marked with a specific tag or analytic account.
  - Allow multiple aggregated lines per document (one per group), instead
    of a single line per document.

- **Validation and warnings**

  Add checks and warnings when line grouping is enabled but:

  - Lines have heterogeneous tax codes that may lead to inaccurate
    results in AvaTax.
  - The document does not match the expected “single sale” / “working
    unit” business rules defined by the company.

- **Extended jurisdiction coverage**

  Document and test line grouping behaviour for additional jurisdictions
  and tax rules where a cap or special treatment applies to a total
  transaction amount (beyond the initial US use cases).

- **Monitoring and logging**

  Improve logging and diagnostics for grouped transactions, making it
  easier for users and accountants to review:

  - The original line breakdown in Odoo.
  - The single-line payload sent to AvaTax.
  - The returned tax amounts and how they are mapped back to Odoo lines.
