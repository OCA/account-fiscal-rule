# -*- coding: utf-8 -*-
# @ 2019 Akretion - www.akretion.com.br -
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        result = super(StockMove, self)._get_new_picking_values()

        result['fiscal_position_id'] = \
            self.procurement_id.sale_line_id.order_id.fiscal_position_id and \
            self.procurement_id.sale_line_id.order_id.fiscal_position_id.id
        return result
