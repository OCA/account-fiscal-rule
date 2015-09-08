# -*- encoding: utf-8 -*-
from . import model

from openerp import SUPERUSER_ID

def create_fiscal_classification_from_product_template(cr, registry):
    """Generate Fiscal Classification for each combinations of Taxes set
    in product"""
    uid = SUPERUSER_ID
    pt_obj = registry['product.template']
    fc_obj = registry['account.product.fiscal.classification']

    # Get all Fiscal Classification (if update process)
    list_res = {}
    fc_ids = fc_obj.search(
        cr, uid, ['|', ('active', '=', False), ('active', '=', True)])
    fc_list = fc_obj.browse(cr, uid, fc_ids)
    for fc in fc_list:
        list_res[fc.id] = [
            fc.company_id and fc.company_id.id or False,
            sorted([x.id for x in fc.sale_tax_ids]),
            sorted([x.id for x in fc.purchase_tax_ids])]

    # Get all product template without Fiscal Classification defined
    pt_ids = pt_obj.search(cr, uid, [
        ('fiscal_classification_id', '=', False)])

    pt_list = pt_obj.browse(cr, uid, pt_ids)
    counter = 0
    total = len(pt_list)
    # Associate product template to existing or new Fiscal Classification
    for pt in pt_list:
        counter += 1
        args = [
            pt.company_id and pt.company_id.id or False,
            sorted([x.id for x in pt.taxes_id]),
            sorted([x.id for x in pt.supplier_taxes_id])]
        if args not in list_res.values():
            _logger.info(
                """create new Fiscal Classification. Product templates"""
                """ managed %s/%s""" % (counter, total))
            fc_id = fc_obj.find_or_create(cr, uid, *args)
            list_res[fc_id] = args
            # associate product template to the new Fiscal Classification
            pt_obj.write(cr, uid, [pt.id], {
                'fiscal_classification_id': fc_id})
        else:
            # associate product template to existing Fiscal Classification
            pt_obj.write(cr, uid, [pt.id], {
                'fiscal_classification_id': list_res.keys()[
                    list_res.values().index(args)]})
