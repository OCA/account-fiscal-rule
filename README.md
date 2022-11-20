
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/account-fiscal-rule&target_branch=13.0)
[![Pre-commit Status](https://github.com/OCA/account-fiscal-rule/actions/workflows/pre-commit.yml/badge.svg?branch=13.0)](https://github.com/OCA/account-fiscal-rule/actions/workflows/pre-commit.yml?query=branch%3A13.0)
[![Build Status](https://github.com/OCA/account-fiscal-rule/actions/workflows/test.yml/badge.svg?branch=13.0)](https://github.com/OCA/account-fiscal-rule/actions/workflows/test.yml?query=branch%3A13.0)
[![codecov](https://codecov.io/gh/OCA/account-fiscal-rule/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/account-fiscal-rule)
[![Translation Status](https://translation.odoo-community.org/widgets/account-fiscal-rule-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/account-fiscal-rule-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Fiscal Rules (multi-criteria decision tables)

With its fiscal position mapping, Odoo may have a limited ability to apply the proper taxes and mapping depending on the context, for instance country of origin and destination of the goods and this could put the fiscal burden on the salesperson, not to speak about e-commerce where things should be automatic. This extensible framework makes it possible to select the proper fiscal position to apply according to an extensible flat decision table.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_avatax](account_avatax/) | 13.0.3.4.4 | [![dreispt](https://github.com/dreispt.png?size=30px)](https://github.com/dreispt) | Automatic Tax application using the Avalara Avatax Service
[account_avatax_sale](account_avatax_sale/) | 13.0.2.4.4 |  | Sales Orders with automatic Tax application using Avatax
[account_fiscal_position_autodetect_optional_vies](account_fiscal_position_autodetect_optional_vies/) | 13.0.1.0.2 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Account Fiscal Position Autodetect optional VIES
[account_fiscal_position_partner_type](account_fiscal_position_partner_type/) | 13.0.1.1.0 |  | Account Fiscal Position Partner Type
[account_fiscal_position_rule](account_fiscal_position_rule/) | 13.0.1.2.1 |  | Account Fiscal Position Rule
[account_fiscal_position_rule_purchase](account_fiscal_position_rule_purchase/) | 13.0.1.0.0 |  | Account Fiscal Position Rule Purchase
[account_fiscal_position_rule_sale](account_fiscal_position_rule_sale/) | 13.0.1.0.1 |  | Account Fiscal Position Rule Sale
[account_multi_vat](account_multi_vat/) | 13.0.1.0.0 | [![ThomasBinsfeld](https://github.com/ThomasBinsfeld.png?size=30px)](https://github.com/ThomasBinsfeld) | Allows setting multiple VAT numbers on any partner and select the right one depending on the fiscal position and delivery address of the invoice.
[account_multi_vat_sale](account_multi_vat_sale/) | 13.0.1.0.2 | [![ThomasBinsfeld](https://github.com/ThomasBinsfeld.png?size=30px)](https://github.com/ThomasBinsfeld) | Determines the tax administration from the delivery address of the invoice.
[account_product_fiscal_classification](account_product_fiscal_classification/) | 13.0.1.0.0 |  | Simplify taxes management for products
[account_product_fiscal_classification_test](account_product_fiscal_classification_test/) | 13.0.1.0.0 |  | tests account_product_fiscal_classification module
[l10n_eu_oss](l10n_eu_oss/) | 13.0.1.1.1 |  | L10n EU OSS

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
