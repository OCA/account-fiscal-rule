# -*- encoding: utf-8 -*-
# Copyright 2021 Rodrigo Bonilla <rodrigo.bonilla@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, SUPERUSER_ID
from openerp.tools import float_compare
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _logger.info("UPDATE ACCOUNT TAX OSS")
        prec = env["decimal.precision"].precision_get("Account")
        account_tax_env = env['l10n.eu.oss.wizard']
        companies = env['res.company'].search([])
        for company in companies:
            taxes = env['account.tax'].search([
                ('oss_country_id', '!=', False),
                ('company_id', '=', company.id)
            ])
            for tax in taxes:
                code_bi = account_tax_env._upgrade_tax_code(
                    tax.oss_country_id, tax.amount, "TB", company,
                )
                if not tax.base_code_id or not tax.ref_base_code_id:
                    tax.write({
                        "base_code_id": code_bi.id,
                        "base_sign": 1,
                        "ref_base_code_id": code_bi.id,
                        "ref_base_sign": -1,
                    })
                code_c = account_tax_env._upgrade_tax_code(
                    tax.oss_country_id, tax.amount, "C", company,
                )
                if not tax.tax_code_id or not tax.ref_tax_code_id:
                    tax.write({
                        "tax_code_id": code_c.id,
                        "tax_sign": 1,
                        "ref_tax_code_id": code_c.id,
                        "ref_tax_sign": -1,
                    })
                # Fill tax codes in journal items
                inv_lines = env["account.invoice.line"].search([
                    ("invoice_line_tax_id", "=", tax.id),
                ])
                # TODO: Handle more than one tax per invoice
                # Tax base
                for inv_line in inv_lines:
                    lines = inv_line.invoice_id.move_id.line_id.filtered(
                        lambda x: (
                            x.account_id == inv_line.account_id
                            and (
                                x.amount_currency
                                and not float_compare(
                                    abs(x.amount_currency),
                                    inv_line.price_subtotal,
                                    precision_digits=prec,
                                )
                                or not float_compare(
                                    abs(x.debit or x.credit),
                                    inv_line.price_subtotal,
                                    precision_digits=prec,
                                )
                            )
                        )
                    )
                    for line in lines:
                        line.write({
                            "tax_code_id": code_bi.id,
                            "tax_amount": line.debit or line.credit,
                        })
                # Tax fee
                for invoice in inv_lines.mapped("invoice_id"):
                    line = invoice.move_id.line_id.filtered("tax_amount")
                    line.write({"tax_code_id": code_c.id})
