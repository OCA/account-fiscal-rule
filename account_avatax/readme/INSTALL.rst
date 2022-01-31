Before installing the Avatax app, the Avalara Python client
must be installed in your system.
It is available at https://pypi.org/project/Avalara.

Typically it can be installed in your system usin ``pip``::

    pip3 install Avalara

The base app, ``account_Avatax``, adds Avatax support to Customer Invoices.
Inthe official app store: https://apps.odoo.com/apps/modules/15.0/account_avatax/

The ``account_avatax_sale`` extension adds support to Quotations / Sales Orders.
Inthe official app store: https://apps.odoo.com/apps/modules/15.0/account_avatax_sale/

In most cases you will want to download and install both modules.

To install the Avatax app:

- Download the AvaTax modules
- Extract the downloaded files
- Upload the extracted directories into your Odoo module/addons directory
- Log into Odoo as an Administrator and enable the Developer Mode, in 'Settings'
- Navigate to 'Apps', select the 'Update Apps List' menu, to have the new apps listed.
- In the Apps list, search for 'AvaTax'
- Click on the Install button. If available, the ``account_avatax_sale`` module will
  also be installed automatically.
