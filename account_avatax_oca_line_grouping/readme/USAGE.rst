This addon does not change **how** you create or validate
Sales Orders and Customer Invoices in Odoo.
It only changes **what is sent to AvaTax** when
*Group document lines for AvaTax* is enabled.

Prerequisites
-------------

- ``account_avatax_oca`` (and optionally ``account_avatax_sale_oca``)
  are installed and correctly configured.
- Fiscal Positions, AvaTax API connection, Products and Customers
  are already working with AvaTax in the standard way.
- The company option **Group document lines for AvaTax** is enabled
  in **Accounting/Invoicing >> Configuration >> AvaTax >> AvaTax API**.

Customer Invoices (grouped)
---------------------------

When **Group document lines for AvaTax** is enabled, customer invoices
still follow the standard AvaTax flow, but the **payload** sent to AvaTax
is different.

- You create an invoice as usual in:

  - **Accounting / Invoicing >> Customers >> Invoices**

- You add as many lines as needed (products, quantities, discounts).
- You ensure the fiscal position and AvaTax tax are correctly set
  (same as with the base connector).
- When you click **Validate**:

  - The connector computes taxes through AvaTax.
  - Instead of sending one line per invoice line, it sends a **single**
    aggregated line, representing the **total untaxed amount** of
    the invoice.
  - AvaTax returns tax for that single line, and the connector maps
    the resulting tax amount back to the **first invoice line**.

Effects in Odoo
---------------

- The **invoice total** (tax included) reflects tax calculated on the
  **entire document**, rather than per line.
- The **first invoice line** will show the AvaTax tax result
  (tax lines are attached to that line).
- Remaining invoice lines do not carry separate tax amounts, but the
  overall accounting is correct.

Effects in AvaTax
------------------

In the AvaTax transaction log:

- You will see **one line** for the invoice with ``quantity = 1`` and
  ``amount = total untaxed amount`` of the invoice, using the item code /
  tax code of the first invoice line’s product (or a fallback code if no
  product is set).
- The transaction status (Uncommitted / Committed / Voided) behaves as
  usual and is controlled by the base connector.


Refunds and credit notes
--------------------------------

Customer refunds (credit notes) behave like invoices:

- If line grouping is enabled, the refund is also sent as a **single**
  aggregated line with a negative amount.
- AvaTax will show a transaction with one line and a negative total,
  consistent with standard refund behaviour, but using the grouped base.

Sales Orders (grouped)
----------------------

When using ``account_avatax_sale_oca`` together with this module,
Sales Orders can also use grouped tax computation.

- You create a Sales Order in:

  - **Sales >> Orders >> Orders**

- You add multiple lines (products, quantities, discounts).
- When you:

  - Confirm the order, or
  - Use **Action >> Update taxes with AvaTax**

  the connector:

  - Aggregates all order lines into a **single** virtual line.
  - Sends one line to AvaTax with:

    - ``qty = 1``
    - ``amount = total untaxed amount`` of the order
    - Combined discount amount if any lines have discounts.
  - Retrieves the tax amount and updates the order accordingly.

- As with the base module, Sales Orders are typically **not** recorded
  as committed transactions in the AvaTax dashboard; they are used to
  estimate tax, and the real transaction is created on invoice.

Effects in Odoo


- From the user perspective, creating and managing Sales Orders does
  not change.
- Tax amounts on the order are computed on the **total** of all lines,
  rather than line by line, when grouping is active.

Effects in AvaTax
-----------------

- The request sent to AvaTax during tax calculation is a single line
  representing the full order.
- The tax result is then used in Odoo for that order’s totals.
- The behaviour of recording / not recording transactions in AvaTax
  follows the logic of the base addon (orders vs invoices).

Practical Example
-----------------

1. Create a Sales Order with several lines that together form a
   single project / working unit (e.g. all materials for one roof).
2. Ensure the company has **Group document lines for AvaTax** enabled.
3. Confirm the order or use **Update taxes with AvaTax**:
   - Odoo shows a total tax based on the **entire order**.
4. Create and validate the Customer Invoice from that order:
   - The invoice sends **one line** to AvaTax with the total base.
   - AvaTax applies tax (and any applicable caps) on the total.
   - In Odoo, the first invoice line carries the tax result.

When NOT to Use Line Grouping
-----------------------------

You should **not** enable the grouping option if:

- Different lines need **different AvaTax product tax codes**
  that must be distinguished by AvaTax.
- The invoice mixes goods and services that should be taxed
  differently at the line level.
- Your tax advisor requires per-line tax visibility in AvaTax.

In those cases, simply disable **Group document lines for AvaTax** and
the standard per-line behaviour from ``account_avatax_oca`` will apply.
