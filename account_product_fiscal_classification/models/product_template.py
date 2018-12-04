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

from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv.orm import setup_modifiers


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Field Section
    fiscal_classification_id = fields.Many2one(
        comodel_name='account.product.fiscal.classification',
        string='Fiscal Classification',
        help="Specify the combination of taxes for this product."
        " This field is required. If you dont find the correct Fiscal"
        " Classification, Please create a new one or ask to your account"
        " manager if you don't have the access right.")

    # Overload Section
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        res.write_taxes_setting(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        self.write_taxes_setting(vals)
        return res

    # View Section
    def fields_view_get(
            self, cr, uid, view_id=None, view_type='form', context=None,
            toolbar=False, submenu=False):
        """Set 'fiscal_classification_id' as required by fields_view_get:
        We don't set it by fields declaration in python file, to avoid
        incompatibility with other modules that could have demo data
        without fiscal_classification_id (the bugs will occur depending
        of the order in which the modules are loaded);
        We don't set it by view inheritance in xml file to impact all views
        (form / tree) that could define the model 'product.template';"""
        res = super(ProductTemplate, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='fiscal_classification_id']")
            if nodes:
                nodes[0].set('required', '1')
                setup_modifiers(
                    nodes[0], res['fields']['fiscal_classification_id'])
                res['arch'] = etree.tostring(doc)
        return res

    @api.onchange('fiscal_classification_id')
    def onchange_fiscal_classification_id(self):
        fc = self.fiscal_classification_id
        self.supplier_taxes_id = [[6, 0, fc.purchase_tax_ids.ids]]
        self.taxes_id = [[6, 0, fc.sale_tax_ids.ids]]

    # Custom Section
    def write_taxes_setting(self, vals):
        """If Fiscal Classification is defined, set the according taxes
        to the product(s); Otherwise, find the correct Fiscal classification,
        depending of the taxes, or create a new one, if no one are found."""
        fc_id = vals.get('fiscal_classification_id', False)
        if fc_id:
            # update or replace 'taxes_id' and 'supplier_taxes_id'
            fc_obj = self.env['account.product.fiscal.classification']
            fc = fc_obj.browse(fc_id)
            tax_vals = {
                'supplier_taxes_id': [[6, 0, [
                    x.id for x in fc.purchase_tax_ids]]],
                'taxes_id': [[6, 0, [
                    x.id for x in fc.sale_tax_ids]]],
            }
            super(ProductTemplate, self.sudo()).write(tax_vals)
        elif 'supplier_taxes_id' in vals.keys() or 'taxes_id' in vals.keys():
            # product template Single update mode
            fc_obj = self.env['account.product.fiscal.classification']
            if len(self) != 1:
                raise ValidationError(
                    _("You cannot change Taxes for many Products."))
            purchase_tax_ids = [x.id for x in self.sudo().supplier_taxes_id]
            sale_tax_ids = [x.id for x in self.sudo().taxes_id]
            fc_id = fc_obj.find_or_create(
                self.company_id.id, sale_tax_ids, purchase_tax_ids)
            super(ProductTemplate, self.sudo()).write(
                {'fiscal_classification_id': fc_id})
