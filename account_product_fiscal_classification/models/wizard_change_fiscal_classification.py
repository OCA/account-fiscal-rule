# -*- coding: utf-8 -*-
# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


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
        readonly=True)

    new_fiscal_classification_id = fields.Many2one(
        comodel_name='account.product.fiscal.classification',
        string='New Fiscal Classification',
        required=True, domain="[('id', '!=', old_fiscal_classification_id)]")

    # View Section
    @api.multi
    def button_change_fiscal_classification(self):
        self.ensure_one()
        template_obj = self.env['product.template']
        template_ids = [
            x.id for x in self.old_fiscal_classification_id.product_tmpl_ids]
        templates = template_obj.browse(template_ids)
        templates.write({
            'fiscal_classification_id': self.new_fiscal_classification_id.id})
