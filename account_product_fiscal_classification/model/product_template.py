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

from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv.orm import setup_modifiers


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Field Section
    tax_group_id = fields.Many2one(
        'tax.group', string='Taxes Group',
        help="Specify the combination of taxes for this product."
        " This field is required. If you dont find the correct Tax"
        " Group, Please create a new one or ask to your account"
        " manager if you don't have the access right.")

    # Overload Section
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        res.check_coherent_vals(vals)
        return res

    @api.multi
    def write(self, vals):
        super(ProductTemplate, self).write(vals)
        self.check_coherent_vals(vals)
        return True

    # View Section
    def fields_view_get(
            self, cr, uid, view_id=None, view_type='form', context=None,
            toolbar=False, submenu=False):
        """
        Set 'tax_group_id' as required, by UI, to avoid incompatibility
        with other modules that could have demo data without tax_group_id.
        """
        res = super(ProductTemplate, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='tax_group_id']")
            if nodes:
                nodes[0].set('required', '1')
                setup_modifiers(nodes[0], res['fields']['tax_group_id'])
                res['arch'] = etree.tostring(doc)
        return res

    # Custom Section
    def check_coherent_vals(self, vals):
        """If tax group is defined, set the according taxes to the product(s);
        Otherwise, find the correct tax group, depending of the taxes, or
        create a new one, if no one are found.
        """
        if vals.get('tax_group_id', False):
            # update or replace 'taxes_id' and 'supplier_taxes_id'
            tax_vals = {
                'supplier_taxes_id': [[6, 0, [
                    x.id for x in self.tax_group_id.supplier_tax_ids]]],
                'taxes_id': [[6, 0, [
                    x.id for x in self.tax_group_id.customer_tax_ids]]],
                }
            super(ProductTemplate, self.sudo()).write(tax_vals)
        elif 'supplier_taxes_id' in vals.keys() or 'taxes_id' in vals.keys():
            # product template Single update mode
            tg_obj = self.env['tax.group']
            if len(self) != 1:
                raise ValidationError(
                    _("You cannot change Taxes for many Products."))
            supplier_tax_ids = [x.id for x in self.sudo().supplier_taxes_id]
            customer_tax_ids = [x.id for x in self.sudo().taxes_id]
            tg_id = tg_obj.find_or_create(
                self.company_id.id, customer_tax_ids, supplier_tax_ids)
            super(ProductTemplate, self.sudo()).write({'tax_group_id': tg_id})
