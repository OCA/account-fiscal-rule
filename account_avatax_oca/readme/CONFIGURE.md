To configure an Odoo company to use Avatax, follow these steps. Note tha
tsome of them might be configured out of the box for the Odoo default
company.

1.  Configure AvaTax API Connection
2.  Configure Company Taxes
3.  Configure Customers
4.  Configure Products

## Configure Avatax API Connection

Before you can configure the Odoo Avatax connector, you will need some
connection details ready:

- Login to <https://home.avalara.com/>
- Navigate to Settings \>\> All AvaTax Settings. There you will see the
  company details.
- Take note of the Account ID and Company Code
- Navigate to Settings \>\> License and API Keys. In the "Reset License
  Key" tab, click on the "Generate License Key" button, and take note of
  it.

To configure AvaTax connector in Odoo:

- Navigate to: Accounting/Invoicing App \>\> Configuration \>\> AvaTax
  \>\> AvaTax API
- Click on the Create button
- Fill out the form with the elements collected from the AvaTax website:
  - Account ID
  - License Key
  - Service URL: usually Production, or Sandox if you have that
    available.
  - Company Code
- Click the Test Connection button
- Click the Save button

Other Avatax API advanced configurations:

- Tax Calculation tab:
  - Disable Document Recording/Commiting: invoices will not be stored in
    Avalara
  - Enable UPC Taxability: this will transmit Odoo's product ean13
    number instead of its Internal Reference. If there is no ean13 then
    the Internal Reference will be sent automatically.
  - Hide Exemption & Tax Based on shipping address -- this will give
    user ability to hide or show Tax Exemption and Tax Based on shipping
    address fields at the invoice level.
- Address Validation tab:
  - Automatic Address Validation: automatically attempts to validate on
    creation and update of customer record, last validation date will be
    visible and stored
  - Require Validated Addresses: if validation for customer is required
    but not valid, the validation will be forced
  - Return validation results in upper case: validation results will
    return in upper case form
- Advanced tab:
  - Automatically generate missing customer code: generates a customer
    code on creation and update of customer profile
  - Log API requests: enables detailed AvaTax transaction logging within
    application
  - Request Timeout: default is 300ms
  - Countries: countries where AvaTax can be used.

## Configure Company Taxes

Each company linked to AvaTax and their associated warehouses should be
configured to ensure the correct tax is calculated and applied for all
transactions.

Validate Company Address:

- On the AvTax API configuration form, click on the "Company Address"
  link
- On the company address form, click on the "validate" button in the
  "AvaTax" tab

Validate Warehouse Address:

- Navigate to: Inventory \>\> Configuration \>\> Warehouse Management
  \>\> Warehouses
- For each warehouse, open the correspoding from view
- On the Warehouse form, click on the "Address" link
- On the warehouse address form, click on the "validate" button in the
  "AvaTax" tab

Fiscal Positions is what tells the AvaTax connector if the AvaTax
service should be used for a particular Sales Order or Invoice.

Configure Fiscal Position:

- Navigate to: Accounting/Invoicing App \>\> Configuration \>\>
  Accounting \>\> Fiscal Positions
- Ensure there is a Fiscal Position record for the Company, with the
  "Use Avatax API" flag checked

When the appropriate Fiscal Position is being used, and a tax rate is
retrieved form AvaTax, then the corresponding Tax is automatically
created in Odoo using a template tax record, that should have the
appropriate accounting configurations.

Configure Taxes:

- Navigate to: Accounting/Invoicing App \>\> Configuration \>\>
  Accounting \>\> Taxes
- Ensure there is a Tax record for the Company, with the "Is Avatax"
  flag checked (visible in the "Advanced Options" tab). This Tax should
  have:
  - Tax Type: Sales
  - Tax Computation: Percentage of Price
  - Amount: 0.0%
  - Distribution for Invoices: ensure correct account configuration
  - Distribution for Credit Notes: ensure correct account configuration

## Configure Customers

Exemption codes are allowed for users where they may apply (ex. Government entities).  
Navigate to: Accounting or Invoicing App \>\> Configuration \>\> AvaTax
\>\> Exemption Code

The module is installed with 16 predefined exemption codes.  
You can add, remove, and modify exemption codes.

Properly configuring each customer ensures the correct tax is calculated
and applied for all transactions.

Create New Customer

- Navigate to Contacts
- Click Create button

Configure and Validate Customer Address

- Enter Customer Address
- Under AvaTax \>\> Validation, click Validate button
- AvaTax Module will attempt to match the address you entered with a
  valid address in its database. Click the Accept button if the address
  is valid.

Tax Exemption Status

- If the customer is tax exempt, check the box under AvaTax \>\> Tax
  Exemption \>\> Is Tax Exempt and
- Select the desired Tax Exempt Code from the dropdown menu.

## Configure Products

Create product tax codes to assign to products and/or product
categories. Navigate to: Accounting or Invoicing App \>\> Configuration
\>\> AvaTax \>\> Product Tax Codes.

From here you can add, remove, and modify the product tax codes.

Products in Odoo are typically assigned to product categories. AvaTax
settings can also be assigned to the product category when a product
category is created.

- Create New Product Category
  - Navigate to: Inventory \>\> Configuration \>\> Products \>\> Product
    Categories
  - Click Create button
- Configure Product Category Tax Code
  - Under AvaTax Properties \>\> Tax Code
  - Select the desired Tax Code
