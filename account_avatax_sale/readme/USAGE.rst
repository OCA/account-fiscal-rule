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


Tax Exemption Status

- Tax exemption status can be defined on Contacts.

- In a multi-company environment, the exemption status is defined per
  Company, since each individual company is required to secure the
  exemption certificates to claim for exemption application,
  and this may not be the case for all Companies.

- If the customer is tax exempt, in the "Avatax" tab, check the "Is Tax Exempt" checkbox.
  When checked, the exemption details can be provided.
  The Exemption Code is the type of exemption,
  and the Exemption Number is an identification number to use on the customer's State.

- This exemption status will only be applied for delivery addresses
  in the State matching the State of the exemption address.
  The same customer can have exemptiions on several states.
  For this use additional Contact/Addresses for those states,
  and enter the exempention details there.

- To make this data management simpler, is it possible to set the customer as exempt
  country wide, using the corresponding checkbox. In this case the exemption status will
  be used for delivery addresses in any state. Using this option has compliance risks, so
  plase use it with care.
