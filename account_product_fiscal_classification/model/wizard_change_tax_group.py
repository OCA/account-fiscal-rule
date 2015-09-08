# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Product - Fiscal Classification module for Odoo
#    Copyright (C) 2014-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class WizardChangeTaxGroup(models.TransientModel):
    """Wizard to allow to change the Taxes Group of products."""
    _name = 'wizard.change.tax.group'

    # Getter / Setter Section
    def _default_old_tax_group_id(self):
        return self.env.context.get('active_id', False)

    # Field Section
    old_tax_group_id = fields.Many2one(
        comodel_name='tax.group', string='Old Taxes Group',
        default=_default_old_tax_group_id, required=True, readonly=True)

    new_tax_group_id = fields.Many2one(
        comodel_name='tax.group', string='New Taxes Group', required=True,
        domain="""[('id', '!=', old_tax_group_id)]""")

    # View Section
    @api.multi
    def button_change_tax_group(self):
        pt_obj = self.env['product.template']
        for wizard in self:
            pt_ids = [x.id for x in wizard.old_tax_group_id.product_tmpl_ids]
            pt_lst = pt_obj.browse(pt_ids)
            pt_lst.write({'tax_group_id': wizard.new_tax_group_id.id})
