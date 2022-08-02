Customer Invoices
~~~~~~~~~~~~~~~~~

The AvaTax module is integrated into Sales Invoices
and is applied to each transaction.
The transaction log in the AvaTax dashboard shows the invoice details
and displays whether the transaction is in an uncommitted or committed status.

A validated invoice will have a Committed status
and a cancelled invoice will have a Voided status.

The module will check if there is a selected warehouse
and will automatically determine the address of the warehouse
and the origin location.
If no address is assigned to the warehouse, the company address is used.

Discounts are handled when they are enabled in Odoo's settings.
They are calculated as a net deduction on the line item cost
before the total is sent to AvaTax.

Create New Customer Invoice
+++++++++++++++++++++++++++

- Navigate to: Accounting or Invoicing >> Customers >> Invoices.
- Click Create button.

Validate Invoice
++++++++++++++++

- Ensure that Tax based on shipping address is checked.
- Line items should have AVATAX selected under Taxes for internal records.
- To complete the invoice, click the Validate button.
- The sale order will now appear in the AvaTax dashboard.

Register Payment
++++++++++++++++

- Click the Register Payment button to finalize the invoice.


Customer Refunds
~~~~~~~~~~~~~~~~

Odoo applies refunds as opposed to voids in its accounting module.
As with customer invoices, the AvaTax module is integrated
with customer refunds and is applied to each transaction.

Refunded invoice transactions will be indicated
 with a negative total in the AvaTax interface.

Initiate Customer Refund

- Navigate to: Accounting or Invoicing >> Customers >> Invoices
- Select the invoice you wish to refund
- Click Add Credit Note button

Create Credit Note

- Under Credit Method, select Create a draft credit note.
- Enter a reason.
- Click Add Credit Note button.

Note: You will be taken to the Credit Notes list view

Validate Refund

- Select the Credit Note you wish to validate, review and then click Validate button.

Register Refund Payment

- Click Register Payment button to complete a refund


Sales Orders
~~~~~~~~~~~~

The AvaTax module is integrated into Sales Orders and allows computation of taxes.
Sales order transactions do not appear in the in the AvaTax interface.

The information placed in the sales order will automatically pass to the invoice
 on the Avalara server and can be viewed in the AvaTax control panel.

Discounts are handled when they are enabled in Odoo's settings.
They will be reported as a net deduction on the line item cost.

Create New Sales Order

- Navigate to: Sales >> Orders >> Orders
- Click Create button

Compute Taxes with AvaTax

- The module will calculate tax when the sales order is confirmed,
  or by navigating to Action >> Update taxes with Avatax.
  At this step, the sales order will retrieve the tax amount from Avalara
  but will not report the transaction to the AvaTax dashboard.
  Only invoice, refund, and payment activity are reported to the dashboard.
- The module will check if there is a selected warehouse
  and will automatically determine the address of the warehouse
  and the origin location. If no address is assigned to the warehouse
  the module will automatically use the address of the company as its origin.
  Location code will automatically populate with the warehouse code
  but can be modified if needed.
