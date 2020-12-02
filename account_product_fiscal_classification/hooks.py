# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def create_fiscal_classification_from_product_template(cr, registry):
    """Generate Fiscal Classification for each combinations of Taxes set
    in product"""
    env = api.Environment(cr, SUPERUSER_ID, {})

    template_obj = env["product.template"]
    classification_obj = env["account.product.fiscal.classification"]

    classifications_keys = {}

    # Get all product template
    templates = template_obj.search(
        ["|", ("active", "=", False), ("active", "=", True)]
    )

    counter = 0
    total = len(templates)
    # Associate product template to Fiscal Classifications
    for template in templates:
        counter += 1
        arg_list = [
            template.company_id and template.company_id.id or False,
            sorted([x.id for x in template.taxes_id]),
            sorted([x.id for x in template.supplier_taxes_id]),
        ]
        if arg_list not in classifications_keys.values():
            _logger.info(
                """create new Fiscal Classification. Product templates"""
                """ managed %s/%s""" % (counter, total)
            )
            classification_id = classification_obj.find_or_create(*arg_list)
            classifications_keys[classification_id] = arg_list
            # associate product template to the new Fiscal Classification
            template.fiscal_classification_id = classification_id
        else:
            # associate product template to existing Fiscal Classification
            fiscal_classification_id = False
            for k, v in classifications_keys.items():
                if v == arg_list:
                    fiscal_classification_id = k
                    break
            template.fiscal_classification_id = fiscal_classification_id
