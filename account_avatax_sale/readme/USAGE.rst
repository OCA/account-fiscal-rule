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
