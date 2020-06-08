To Configure AvaTax API:

- Navigate to: Accounting or Invoicing App >> Configuration >> AvaTax >> AvaTax API
- Click the Create button.
- Uncheck the Disable AvaTax Calculation box
- Fill out the form with your Company Code, Account Number, and License Key
   as provided with your Avalara account
- Select the proper service URL provided to you by Avalara: test or production.
- Click the Test Connection button
- Click the Save button

Other Avatax API advanced configurations:

- Adapter

  - Request Timeout -- default is 300ms
  - Enable Logging -- enables detailed AvaTax transaction logging within application

- Address Validation

  - Disable Address Validation
  - Address Validation on save for customer profile -- automatically attempts
    to validate on creation and update of customer profile,
    last validation date will be visible and stored
  - Force Address Validation -- if validation for customer is required but not valid,
    the validation will be forced
  - Return validation results in upper case -- validation results
    will return in upper case form
  - Automatically generate customer code -- generates a customer code
    on creation and update of customer profile

- Avalara Submissions/Transactions

  - Disable Avalara Tax Commit -- validated invoices will not be sent to Avalara
  - Enable UPC Taxability -- this will transmit Odoo's product ean13 number
    instead of its Internal Reference. If there is no ean13
    then the Internal Reference will be sent automatically.

- Countries

    - Add or remove applicable countries -- the calculator will not calculate
      for a country unless it's on the list.

Configure Exemption Codes
~~~~~~~~~~~~~~~~~~~~~~~~~

Exemption codes are allowed for users where they may apply (ex. Government entities).
 Navigate to: Accounting or Invoicing App >> Configuration >> AvaTax >> Exemption Code

The module is installed with 16 predefined exemption codes.
 You can add, remove, and modify exemption codes.

Product Tax Codes
~~~~~~~~~~~~~~~~~

Create product tax codes to assign to products and/or product categories.
Navigate to: Accounting or Invoicing App >> Configuration >> AvaTax >> Product Tax Codes.

From here you can add, remove, and modify the product tax codes.


Configure Taxes
~~~~~~~~~~~~~~~

The AvaTax module is integrated into the tax calculation of Odoo.
AVATAX is automatically added as a type of taxes to be applied.
You can configure how AVATAX integrates within the Odoo system.

Configure AVATAX Tax Type:

- Navigate to: Accounting or Invoicing App >> Configuration >> Accounting >> Taxes
- Select AVATAX from the list view (automatically added on module install).
- Click the Edit button to configure the AVATAX Tax Type
  with the proper tax account configuration for your system.

Note: Upon initial install the settings will be blank.
The image shows the demo configuration.


Product Category Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Products in Odoo are typically assigned to product categories.
AvaTax settings can also be assigned to the product category
when a product category is created.

- Create New Product Category

  - Navigate to: Inventory >> Configuration >> Products >> Product Categories
  - Click Create button

- Configure Product Category Tax Code

  - Under AvaTax Properties >> Tax Code
  - Select the desired Tax Code


Company Configuration
~~~~~~~~~~~~~~~~~~~~~

Each company linked to AvaTax and their associated warehouses
should be configured to ensure the correct tax is calculated
and applied for all transactions.

Warehouse Configuration

- Navigate to: Inventory >> Configuration >> Warehouse Management >> Warehouses
- Select the warehouse associated with your company
- Under Address, follow the link to be directed to your warehouse profile

Configure Warehouse Address

- Enter Warehouse Address
- Under AvaTax >> Validation, click Validate button


Customer Configuration
~~~~~~~~~~~~~~~~~~~~~~

Properly configuring each customer ensures the correct tax is calculated
and applied for all transactions.

Create New Customer

- Navigate to Contacts
- Click Create button

Configure and Validate Customer Address

- Enter Customer Address
- Under AvaTax >> Validation, click Validate button
- AvaTax Module will attempt to match the address you entered
  with a valid address in its database.
  Click the Accept button if the address is valid.

Tax Exemption Status

- If the customer is tax exempt, check the box under
  AvaTax >> Tax Exemption >> Is Tax Exempt and
- Select the desired Tax Exempt Code from the dropdown menu.
