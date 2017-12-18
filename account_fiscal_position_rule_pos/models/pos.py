# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, api


class POSOrder(models.Model):
    _inherit = 'pos.order'

    def _fiscal_position_map(self, **kwargs):
        return self.env['account.fiscal.position.rule'].with_context(
            use_domain=('use_sale', '=', True)).apply_fiscal_mapping(**kwargs)

    @api.onchange('company_id', 'partner_id')
    def onchange_fiscal_position_map(self):
        """Retrieve `fiscal_position_id` via rules."""
        kwargs = {
            'company_id': self.company_id,
            'partner_id': self.partner_id,
        }

        obj_fiscal_position = self._fiscal_position_map(**kwargs)
        if obj_fiscal_position and \
                obj_fiscal_position != self.fiscal_position_id:
            self.fiscal_position_id = obj_fiscal_position.id
