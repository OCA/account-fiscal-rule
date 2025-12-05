Once configured:

1.  Create a Sales Order, Purchase Order, or Invoice.
2.  Select a Product Variant that has a specific tax amount configured.
3.  Add the corresponding tax (the one with "Use Product Amount" checked) to the line.

> **Note**: If the tax is set as a Default Tax on the product, it will be added automatically.

4.  Odoo will compute the tax amount based on the value defined for the selected variant.
5.  If you change the quantity, the fixed tax amount is multiplied by the quantity (e.g., 2 units * 1.50€ = 3.00€ tax).
