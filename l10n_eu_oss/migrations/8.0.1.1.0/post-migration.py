# -*- encoding: utf-8 -*-
# Copyright 2021 Rodrigo Bonilla <rodrigo.bonilla@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _logger.info("UPDATE ACCOUNT TAX OSS")
        account_tax_env = env['l10n.eu.oss.wizard']
        res_company_ids = env['res.company'].search([])
        for res_company_id in res_company_ids:
            account_tax_ids = env['account.tax'].search([
                ('oss_country_id', '!=', False),
                ('company_id', '=', res_company_id.id)
                ])
            for account_tax_id in account_tax_ids:
                if not account_tax_id.base_code_id and \
                        not account_tax_id.ref_base_code_id:
                    code_bi = account_tax_env._upgrade_tax_code(
                        account_tax_id.oss_country_id, account_tax_id.amount,
                        'TB')
                    if code_bi.company_id.id != res_company_id.id:
                        code_bi = code_bi.copy({
                            'company_id': res_company_id.id})
                    account_tax_id.write({
                        "base_code_id": code_bi.id,
                        "base_sign": 1,
                        "ref_base_code_id": code_bi.id,
                        "ref_base_sign": -1,
                    })
                if not account_tax_id.tax_code_id and \
                        not account_tax_id.ref_tax_code_id:
                    code_c = account_tax_env._upgrade_tax_code(
                        account_tax_id.oss_country_id, account_tax_id.amount,
                        'C')
                    if code_c.company_id.id != res_company_id.id:
                        code_c = code_c.copy({
                            'company_id': res_company_id.id})
                    account_tax_id.write({
                        "tax_code_id": code_c.id,
                        "tax_sign": 1,
                        "ref_tax_code_id": code_c.id,
                        "ref_tax_sign": -1,
                    })
