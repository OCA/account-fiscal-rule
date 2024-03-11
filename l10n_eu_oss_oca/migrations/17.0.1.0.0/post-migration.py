# Copyright 2023 Factor Libre S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    oss_taxes = env["account.tax"].search([("oss_country_id", "!=", False)])
    for oss_tax in oss_taxes:
        oss_tax.country_id = oss_tax.company_id.account_fiscal_country_id
