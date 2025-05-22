Since an update in Odoo https://github.com/odoo/odoo/commit/13e9833e0bc809a26843890363586f61a37d061c the case with ecotax as tax included and another tax included does not work anymore.
The ecotax tax should only be used along with price excluded tax, or be configured as price excluded itself.

There is a limitation with the country restriction on ecotax classification when using the account_ecotax_tax and account_ecotax_sale_tax modules.OIt is currently not possible to have multiple classificaiton restricted to different countries for a same product.
