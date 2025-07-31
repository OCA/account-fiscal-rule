# Copyright 2023 Factor Libre S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    oss_taxes = env["account.tax"].search([("oss_country_id", "!=", False)])
    oss_tax_groups = oss_taxes.mapped("tax_group_id")
    for oss_tax_group in oss_tax_groups:
        oss_tax_group.country_id = oss_tax_group.company_id.account_fiscal_country_id
    for oss_tax in oss_taxes:
        oss_tax.country_id = oss_tax.company_id.account_fiscal_country_id
