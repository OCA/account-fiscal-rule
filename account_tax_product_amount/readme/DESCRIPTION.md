This module allows you to manage fixed tax amounts that vary per product variant.

By default, Odoo manages fixed tax amounts at the tax level. However, some taxes effectively depend on product characteristics (like dimensions, weight, or material) while sharing the same tax configuration (same account, same name, same tax report line).

With this module, you can configure a tax with `Amount Type` set to `Fixed` and enable the **Use Product Amount** option. This tells Odoo to look for the specific amount defined on the product variant. If no specific amount is found for the variant, the default amount defined on the tax is used.

**Features:**

*   Define specific tax amounts per product variant.
*   Support for multiple taxes per product.
*   Multi-company support.
*   Compatible with Sales, Purchases, Invoicing, and Website Sales.

> **Note**: This module is particularly useful for handling **Eco-taxes** (or similar levies) and offers advantages over other community modules:
>
> *   Compared to `account_ecotax`: This module relies on the standard Odoo Tax engine. This makes it natively compatible with accounting, invoicing, and reporting without needing glue modules for every application (Sales, Purchase, POS, etc.). It also allows using different accounts per tax easily.
> *   Compared to `account_ecotax_tax`: This module does not rely on `account_tax_python` (Python Code taxes), which can be complex to maintain. It also supports multiple different tax amounts for a single variant independently and offers better flexibility.
