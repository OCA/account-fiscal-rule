To configure this module, you need to:

1.  **Configure Accounts**: Setup specific accounts for your taxes in your Chart of Accounts, or decide which existing accounts to use.

2.  **Create a Tax**:

    *   Go to **Accounting > Configuration > Taxes**.
    *   Create a new tax.
    *   Set **Tax Computation** (Amount Type) to `Fixed`.
    *   Check the box **Use Product Amount**.
    *   Set a default **Amount**. This will be used as a fallback if no specific amount is set on the product variant.
    *   Configure other settings (Accounts, Tax Group, Label on Invoices, etc.) as usual.

3. **Add tax on product template**:

    *   Go to **Product template** form view.
    *   Select the product template.
    *   Add the tax to the **Sales/Purchase Taxes** field.
    *   Save the record this will generate the tax amount records for all existing variants using the default tax amount.

4.  **Define Amounts on Products**:

    *   Go to the **Product Variant** form view.
    *   You will find a new tab or section (depending on view configuration) to set the fixed amounts for each tax that has "Use Product Amount" enabled.
    *   Alternatively, go to **Accounting > Configuration > Accounting > Tax > Product Amounts** to see and manage all product tax amounts in one place.


**Eco-Tax Example (France)**

In France, the "Éco-participation" (Eco-tax) is a fixed contribution added to the price of new items to fund recycling and waste management. The amount depends on the product's characteristics (weight, type, material).

*Scenario*: You sell a sofa that contains electronic components (e.g., a massage sofa). This product is subject to two distinct eco-taxes: one for the furniture (Eco-mobilier) and one for the electronics (DEEE).

1.  **Purchase**: When you buy the goods, the eco-tax is billed by your supplier. It is not recoverable VAT but an expense spread over the product cost.
    *   We advise using a dedicated Expense Account (e.g., `607...`) for each tax or a generic one to track these costs.

2.  **Sale**: When you sell the product, you collect the eco-tax from the customer.
    *   Use a dedicated Income Account (e.g., `707...` or a liability account depending on your accounting rules) for the tax.
    *   Since the Eco-tax is part of the taxable basis for VAT, ensure that the Eco-tax is applied *before* VAT.
    *   In the Tax configuration, for the VAT tax, ensure "Affect Base of Subsequent Taxes" is checked (or simply ensure the Eco-tax is in a Tax Group with lower sequence/sequence number so it applies first, and VAT applies on top).

*Calculation Example*:
*   Sofa Base Price: 10.00€
*   Eco-mobilier (Furniture Tax): 1.50€
*   VAT (20%): Applied on (10.00€ + 1.50€) = 11.50€ * 20% = 2.30€
*   **Total Price**: 10.00€ + 1.50€ + 2.30€ = 13.80€

*Journal Entries*:
*   **Credit** 707000 Product Sales: 10.00€
*   **Credit** 707100 Eco-tax Income (or similar): 1.50€
*   **Credit** 445700 Output VAT: 2.30€
*   **Debit** 411100 Customer Receivable: 13.80€
