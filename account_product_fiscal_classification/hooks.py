# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def create_fiscal_classification_from_product_template(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    AccountTax = env["account.tax"]
    AccountProductFiscalClassification = env["account.product.fiscal.classification"]
    template_values = (
        env["product.template"]
        .with_context(active_test=False)
        .search_read(
            domain=[("fiscal_classification_id", "=", False)],
            fields=["company_id", "taxes_id", "supplier_taxes_id"],
        )
    )
    dict_key_template_ids = {}
    for template_value in template_values:
        key = (
            frozenset(template_value["taxes_id"]),
            frozenset(template_value["supplier_taxes_id"]),
        )
        if key in dict_key_template_ids.keys():
            dict_key_template_ids[key].append(template_value["id"])
        else:
            dict_key_template_ids[key] = [template_value["id"]]

    for (sale_tax_ids, purchase_tax_ids), template_ids in dict_key_template_ids.items():
        sale_taxes = AccountTax.browse(sale_tax_ids)
        purchase_taxes = AccountTax.browse(purchase_tax_ids)
        vals = AccountProductFiscalClassification._prepare_vals_from_taxes(
            purchase_taxes, sale_taxes
        )
        _logger.info(
            f"Creating new Fiscal Classification '{vals['name']}'"
            f" for {len(template_ids)} templates ..."
        )

        classification = AccountProductFiscalClassification.create(vals)
        query = """
            UPDATE product_template
            SET fiscal_classification_id = %s
            WHERE id in %s
        """
        params = (
            classification.id,
            tuple(
                template_ids,
            ),
        )
        env.cr.execute(query, params=params)
