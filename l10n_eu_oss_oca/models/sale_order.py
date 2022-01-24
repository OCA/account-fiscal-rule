# Copyright 2021 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('company_id.account_fiscal_country_id', 'fiscal_position_id.country_id', 'fiscal_position_id.foreign_vat')
    def _compute_tax_country_id(self):

        oss_sale_order_ids = self.filtered(
            lambda a: a.fiscal_position_id and a.fiscal_position_id.oss_oca
        )
        for record in oss_sale_order_ids:
            record.tax_country_id = record.fiscal_position_id.country_id
        super(SaleOrder, self-oss_sale_order_ids)._compute_tax_country_id()
