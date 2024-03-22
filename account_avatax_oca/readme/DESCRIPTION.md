**AVALARA CERTIFICATION PENDING!**

Odoo provides integration with AvaTax, a tax solution software by
Avalara which includes sales tax calculation for all US states and
territories and all Canadian provinces and territories (including GST,
PST, and HST).

This module is capable of automatically detecting origin (Output
Warehouse) and destination (Client Address), then calculating and
reporting taxes to the user's Avalara account as well as a recording the
correct sales taxes for the validated addresses within Odoo ERP.

This module is compatible both with the Odoo Enterprise and Odoo
Community editions.

An Avatax account is needed. Account information to access the Avatax
dashboard can be obtained through the Avalara website here:
<https://www.avalara.com/products/calculations.html>

Once configured, the module operates in the background and performs
calculations and reporting seamlessly to the AvaTax server.

This guide includes instructions for the following elements:

- Activating your organization's AvaTax account and downloading the
  product
- Entering the AvaTax credentials into your Odoo database and
  configuring it to use AvaTax services and features within Odoo

Note: Test the module before deploying in live environment. All changes
to the AvaTax settings must be performed by a user with administrative
access rights.

**IMPORTANT - resolving name conflict with Odoo EE**

Avatax support was added to Odoo EE 14 and 15. Unfortunately the module
names used are the same as the OCA ones, and because of this name
collision the OCA modules were forced to change name.

The main module was renamed from `account_avatax` (now used by Odoo EE)
to `account_avatax_oca`.

To apply this change in your odoo database and continue using the OCA
Avalara certified connector:

> 1.  Ensure you have the latest version from the OCA, and you see `account_avatax_oca`  
>     in your Apps list.
>
> 2.  Install the new `account_avatax_oca` module
>
> 3.  Unistall the `account_avatax` module
>
> 4.  Confirm that your configurations were kept safe, in particular:  
>     Avatax API, "Avatax" default Fiscal Position, and "Avatax" default
>     Tax record.
