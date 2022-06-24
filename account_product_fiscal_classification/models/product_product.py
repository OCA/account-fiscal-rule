# Copyright (C) 2022-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # View Section
    @api.onchange('fiscal_classification_id')
    def _onchange_fiscal_classification_id(self):
        self.supplier_taxes_id = [(
            6, 0,
            self.fiscal_classification_id.sudo().purchase_tax_ids.ids
        )]
        self.taxes_id = [(
            6, 0,
            self.fiscal_classification_id.sudo().sale_tax_ids.ids
        )]
