# coding: utf-8
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models


class AccountFiscalPositionTemplate(models.Model):
    _inherit = 'account.fiscal.position.template'

    _TYPE_POSITION_USE_SELECTION = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('all', 'All'),
    ]

    type_position_use = fields.Selection(
        string='Position Application',
        selection=_TYPE_POSITION_USE_SELECTION, default='all')

    @api.model
    def generate_fiscal_position(
            self, chart_temp_id, tax_template_ref, acc_template_ref,
            company_id):
        return super(AccountFiscalPositionTemplate, self.with_context(
            chart_template_id=chart_temp_id)).generate_fiscal_position(
            chart_temp_id, tax_template_ref, acc_template_ref,
            company_id)
