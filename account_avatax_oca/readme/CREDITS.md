This module was originally developed by Fabrice Henrion at Odoo SA, and
maintained up to version 11.

For version 12, Fabrice invited partners to migrate this modules to
later version, and maintain it.

Open Source Integrators performed the migration to Odoo 12 , and later
added support for the more up to date REST API , alongside with the
legacy SOAP API.

With the addition of the REST API, a deep refactor was introduced,
changing the tax calculation approach, from just setting the total tax
amount, to instead adding the tax rates to each document line and then
having Odoo do all the other computations.

For Odoo 13, the legacy SOAP support was supported, and additional
refactoring was done to contribute the module to the Odoo Community
Association.
