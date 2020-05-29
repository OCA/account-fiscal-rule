Odoo provides integration with AvaTax, a tax solution software by Avalara
which includes sales tax calculation for all US states and territories
and all Canadian provinces and territories (including GST, PST, and HST).

This module is capable of automatically detecting origin (Output Warehouse)
and destination (Client Address), then calculating and reporting taxes
to the user's Avalara account as well as a recording the correct sales taxes
for the validated addresses within Odoo ERP.

This module is compatible both with the Odoo Enterprise and odoo Community
editions.

An Avatax account is needed. Account information to access
the Avatax dashboard can be obtained through the Avalara website here:
https://www.avalara.com/products/avatax/

Once configured, the module operates in the background and performs
calculations and reporting seamlessly to the AvaTax server.

This guide includes instructions for the following elements:

- Activating your organization's AvaTax account and downloading the product
- Entering the AvaTax credentials into your Odoo database and configuring it
  to use AvaTax services and features within Odoo

Note: Test the module before deploying in live environment.
All changes to the AvaTax settings must be performed by a user with
administrative access rights.
