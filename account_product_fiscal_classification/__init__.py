# -*- coding: utf-8 -*-
from . import models

import logging
from openerp import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def create_fiscal_classification_from_product_template(cr, registry):
    """Generate Fiscal Classification for each combinations of Taxes set
    in product"""
    env = api.Environment(cr, SUPERUSER_ID, {})

    template_obj = env['product.template']
    classification_obj = env['account.product.fiscal.classification']

    classifications_keys = {}

    # Get all product template
    templates = template_obj.search([
        '|', ('active', '=', False), ('active', '=', True)])

    counter = 0
    total = len(templates)
    # Associate product template to Fiscal Classifications
    for template in templates:
        counter += 1
        args = [
            template.company_id and template.company_id.id or False,
            sorted([x.id for x in template.taxes_id]),
            sorted([x.id for x in template.supplier_taxes_id])]
        if args not in classifications_keys.values():
            _logger.info(
                """create new Fiscal Classification. Product templates"""
                """ managed %s/%s""" % (counter, total))
            classification_id = classification_obj.find_or_create(*args)
            classifications_keys[classification_id] = args
            # associate product template to the new Fiscal Classification
            template.fiscal_classification_id = classification_id
        else:
            # associate product template to existing Fiscal Classification
            template.fiscal_classification_id = classifications_keys.keys()[
                classifications_keys.values().index(args)]
