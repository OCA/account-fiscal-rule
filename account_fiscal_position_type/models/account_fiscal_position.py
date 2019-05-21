# coding: utf-8
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    _TYPE_POSITION_USE_SELECTION = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('all', 'All'),
    ]

    type_position_use = fields.Selection(
        string='Position Application',
        selection=_TYPE_POSITION_USE_SELECTION, default='all')

    @api.model
    def create(self, values):
        AccountFiscalPositionTemplate =\
            self.env['account.fiscal.position.template']
        chart_template_id = self.env.context.get('chart_template_id', False)
        if chart_template_id:
            templates = AccountFiscalPositionTemplate.search([
                ('chart_template_id', '=', chart_template_id),
                ('name', '=', values['name'])])

            if len(templates) == 1:
                values.update({
                    'type_position_use': templates[0].type_position_use,
                })
        return super(AccountFiscalPosition, self).create(values)
