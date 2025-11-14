This addon is an extension of the AvaTax connector provided by
``account_avatax_oca``. It does **not** replace the base connector and
depends on it being correctly installed and configured first.

Python dependency
-----------------

The same Python client library used by ``account_avatax_oca`` is required:

- Avalara Python client: https://pypi.org/project/Avalara

If you already installed it for the base module, you do not need to do
anything else. Otherwise, install it with ``pip`` in your Odoo
environment::

    pip3 install Avalara

Module dependencies
-------------------

This module depends on:

- ``account_avatax_oca``  (AvaTax support for Customer Invoices)
- ``account_avatax_sale_oca``  (AvaTax support for Quotations / Sales Orders)

Make sure both are available and installed in your Odoo instance
(or at least ``account_avatax_oca`` if you only use Invoices).

Install the addon
-----------------

To install ``account_avatax_oca_line_grouping``:

1. Clone or download the OCA *account-fiscal-rule* repository (or your fork)
   that contains this addon.
2. Ensure the directory ``account_avatax_oca_line_grouping`` is in your
   Odoo addons path.
3. Restart the Odoo server.
4. Log into Odoo as an Administrator and enable **Developer Mode**
   in *Settings*.
5. Go to **Apps**, click **Update Apps List** so that Odoo detects
   the new addon.
6. Search for **AvaTax Line Grouping** or ``account_avatax_oca_line_grouping``.
7. Click **Install**.

After installation, you can enable the line-grouping behaviour in:

- **Accounting/Invoicing >> Configuration >> AvaTax >> AvaTax API**
  (see the configuration guide for the *Group document lines for AvaTax* option).
