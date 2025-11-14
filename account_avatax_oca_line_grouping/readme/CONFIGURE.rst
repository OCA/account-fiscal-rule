This addon extends the AvaTax connector provided by ``account_avatax_oca``
and allows grouping all document lines (Sales Orders and Customer Invoices)
into a single line when sending data to AvaTax.

This behaviour is useful for “single sale” or bulk / working-unit scenarios,
for example where local rules require applying surtax caps on the **total**
of the invoice instead of per line.

Prerequisites
-------------

Before using this module, you must:

- Install and configure ``account_avatax_oca`` (and ``account_avatax_sale_oca``).
- Follow the configuration steps described in the **CONFIGURE.rst** of
  ``account_avatax_oca`` (AvaTax API connection, company taxes, customers,
  products, fiscal positions, etc.).

Once the base connector is working and taxes are correctly retrieved from AvaTax,
you can enable line grouping as described below.

Enable Line Grouping
--------------------

1. Go to: **Accounting/Invoicing App >> Configuration >> AvaTax >> AvaTax API**.
2. Open the AvaTax configuration used by your company.
3. In the *Tax Calculation* (or equivalent) tab, enable:

   - **Group document lines for AvaTax**

4. Save the configuration.

Functional Behaviour
--------------------

When **Group document lines for AvaTax** is enabled on the company:

For **Sales Orders**:

  - All ``sale.order.line`` records of the order are aggregated.
  - The connector sends a **single line** to AvaTax with ``qty = 1`` and
    ``amount = total untaxed amount of all lines`` (including discounts,
    using the same base as the standard AvaTax computation), and using
    ``itemCode`` and ``taxCode`` taken from the first order line’s product
    (or a fallback identifier if no product is set).
  - A combined discount amount is used if any line has a discount.


- For **Customer Invoices (account.move)**:

  - All invoice lines are aggregated in the same way.
  - Only the **first invoice line** produces an AvaTax payload entry;
    the remaining lines are not sent individually.
  - AvaTax returns tax values for that single line, and the connector
    applies the resulting tax amount to that first line in Odoo.
  - The invoice total (including tax) reflects tax computed on the **entire document**,
    which is required in certain single-sale / bulk / working-unit scenarios.

When the option is **disabled**, the standard behaviour from
``account_avatax_oca`` is used: AvaTax receives one line per Odoo line,
and taxes are calculated line by line.

Usage Notes and Caveats
-----------------------

- Line grouping changes how the tax base is presented to AvaTax
  and can significantly affect calculated taxes and possible surtax caps.
- It should only be enabled when the entire document is legally treated as
  a **single sale** or as a **working unit** (e.g. certain construction
  or bulk material contracts).
- If your invoices contain lines with different taxability types or
  different product tax codes that must be distinguished by AvaTax,
  you should **not** enable line grouping.
- Always consult with your tax advisor before enabling this option
  in a production environment.
