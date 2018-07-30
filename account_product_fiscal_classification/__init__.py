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
    # Don't manage products that should be populated by SQL request before
    templates = template_obj.with_context(active_test=False).search([
        ('fiscal_classification_id', '=', False)])

    counter = 0
    total = len(templates)
    # Associate product template to Fiscal Classifications
    res_list = templates.read(['company_id', 'taxes_id', 'supplier_taxes_id'])
    for res in res_list:
        key = str([
            res['company_id'] and res['company_id'][0],
            res['taxes_id'],
            res['supplier_taxes_id']])
        if key in classifications_keys.keys():
            classifications_keys[key].append(res['id'])
        else:
            classifications_keys[key] = [res['id']]
    for key, value in classifications_keys.iteritems():
        counter += len(value)
        _logger.info(
            "create new Fiscal Classification for %d Product templates"
            " %d / %d" % (len(value), counter, total))
        classification_id = classification_obj.find_or_create(*eval(key))
        sub_templates = templates.browse(value)
        sub_templates.write({'fiscal_classification_id': classification_id})
