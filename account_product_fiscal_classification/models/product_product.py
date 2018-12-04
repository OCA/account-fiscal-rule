# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('fiscal_classification_id')
    def onchange_fiscal_classification_id(self):
        fc = self.fiscal_classification_id
        self.supplier_taxes_id = [[6, 0, fc.purchase_tax_ids.ids]]
        self.taxes_id = [[6, 0, fc.sale_tax_ids.ids]]
