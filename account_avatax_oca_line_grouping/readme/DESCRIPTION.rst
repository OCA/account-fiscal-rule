This addon extends the AvaTax connector provided by
``account_avatax_oca`` (OCA *account-fiscal-rule* repository).

It adds an optional feature to **group all document lines into a single
line** when sending data to AvaTax, so that tax is computed on the
**total document amount** instead of line by line.

This behaviour is useful in jurisdictions where multiple items sold
together are legally treated as a **single sale** or a **working unit**
for tax purposes (for example, some discretionary surtax cap rules
on bulk/material or project invoices).

Main Features
-------------

* Optional company-level setting: **Group document lines for AvaTax**.
* When enabled:

  - For **Sales Orders**:

    - All ``sale.order.line`` records are aggregated.
    - AvaTax receives **one line** with:

      - ``qty = 1``
      - ``amount = total untaxed amount of all lines``
      - ``itemCode`` and ``taxCode`` taken from the first line’s product
        (or a safe fallback if no product is set).
      - A combined discount amount if any line has a discount.

  - For **Customer Invoices (account.move)**:

    - All invoice lines are aggregated in the same way.
    - Only the **first invoice line** generates an AvaTax payload line.
    - AvaTax tax result is applied to that first line in Odoo.
    - The invoice total (including tax) reflects tax on the **entire**
      document, matching single-sale / working-unit requirements.

* When the option is **disabled**, the standard behaviour from
  ``account_avatax_oca`` is preserved: AvaTax receives one line per Odoo line.
