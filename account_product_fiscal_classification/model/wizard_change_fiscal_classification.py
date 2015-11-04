# -*- coding: utf-8 -*-
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


class WizardChangeFiscalClassification(models.TransientModel):
    """Wizard to allow to change the Fiscal Classification of products."""
    _name = 'wizard.change.fiscal.classification'

    # Getter / Setter Section
    def _default_old_fiscal_classification_id(self):
        return self.env.context.get('active_id', False)

    # Field Section
    old_fiscal_classification_id = fields.Many2one(
        comodel_name='account.product.fiscal.classification',
        string='Old Fiscal Classification',
        default=_default_old_fiscal_classification_id,
        required=True, readonly=True)

    new_fiscal_classification_id = fields.Many2one(
        comodel_name='account.product.fiscal.classification',
        string='New Fiscal Classification',
        required=True, domain="[('id', '!=', old_fiscal_classification_id)]")

    # View Section
    @api.one
    def button_change_fiscal_classification(self):
        template_obj = self.env['product.template']
        template_ids = [
            x.id for x in self.old_fiscal_classification_id.product_tmpl_ids]
        templates = template_obj.browse(template_ids)
        templates.write({
            'fiscal_classification_id': self.new_fiscal_classification_id.id})
