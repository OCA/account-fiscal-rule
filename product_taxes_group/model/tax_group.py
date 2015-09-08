# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product - Taxes Group module for Odoo
#    Copyright (C) 2014 -Today GRAP (http://www.grap.coop)
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

import logging

from openerp import SUPERUSER_ID, models, fields, api, _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TaxGroup(models.Model):
    """Group of customer and supplier taxes.
    This group is linked to a product to select a group of taxes in one
    time."""
    _name = 'tax.group'
    _description = 'Taxes Group'
    _MAX_LENGTH_NAME = 256

    # Getter / Setter Section
    def _default_company_id(self):
        return self.env['res.users']._get_company()

    def _get_product_tmpl_qty(self):
        for rec in self:
            rec.product_tmpl_qty = self.env['product.template'].search_count([
                ('tax_group_id', '=', rec.id), '|', ('active', '=', False),
                ('active', '=', True)])

    def _get_product_tmpl_ids(self):
        for rec in self:
            rec.product_tmpl_ids = self.env['product.template'].search([
                ('tax_group_id', '=', rec.id), '|', ('active', '=', False),
                ('active', '=', True)])

    # Field Section
    name = fields.Char(
        size=_MAX_LENGTH_NAME, required=True, select=True)

    company_id = fields.Many2one(
        comodel_name='res.company', default=_default_company_id,
        string='Company', help="Specify a company"
        " if you want to define this Taxes Group only for specific company."
        " Otherwise, this Taxes Group will be available for all companies.")

    active = fields.Boolean(
        default=True,
        help="If unchecked, it will allow you to hide the Taxes"
        " Group without removing it.")

    product_tmpl_ids = fields.One2many(
        comodel_name='product.template', string='Products',
        compute=_get_product_tmpl_ids)

    product_tmpl_qty = fields.Integer(
        string='Products Quantity', compute=_get_product_tmpl_qty)

    supplier_tax_ids = fields.Many2many(
        'account.tax', 'product_supplier_tax_rel',
        'group_id', 'tax_id', string='Supplier Taxes', domain="""[
            ('company_id', '=', company_id),
            ('parent_id', '=', False),
            ('type_tax_use', 'in', ['purchase', 'all'])]""")

    customer_tax_ids = fields.Many2many(
        'account.tax', 'product_customer_tax_rel',
        'group_id', 'tax_id', string='Customer Taxes', domain="""[
            ('company_id', '=', company_id),
            ('parent_id', '=', False),
            ('type_tax_use', 'in', ['sale', 'all'])]""")

    # Overload Section
    @api.multi
    def write(self, vals):
        res = super(TaxGroup, self).write(vals)
        pt_obj = self.env['product.template']
        if 'supplier_tax_ids' in vals or 'customer_tax_ids' in vals:
            for tg in self:
                pt_lst = pt_obj.browse([x.id for x in tg.product_tmpl_ids])
                pt_lst.write({'tax_group_id': tg.id})
        return res

    @api.multi
    def unlink(self):
        for tg in self:
            if tg.product_tmpl_qty != 0:
                raise ValidationError(
                    _("""You cannot delete The taxes Group '%s' because"""
                        """ it contents %s products. Please move products"""
                        """ to another Taxes Group.""") % (
                        tg.name, tg.product_tmpl_qty))
        return super(TaxGroup, self).unlink()

    # Custom Sections
    def find_or_create(self, cr, uid, values, context=None):
        at_obj = self.pool['account.tax']
        # Search for existing Taxes Group
        tg_ids = self.search(
            cr, uid, ['|', ('active', '=', False), ('active', '=', True)],
            context=context)
        for tg in self.browse(cr, uid, tg_ids, context=context):
            if (tg.company_id.id == values[0] and
                sorted([x.id for x in tg.customer_tax_ids]) == values[1] and
                    sorted([x.id for x in tg.supplier_tax_ids]) == values[2]):
                return tg.id

        # create new Taxes Group if not found
        if len(values[1]) == 0 and len(values[2]) == 0:
            name = _('No taxes')
        elif len(values[2]) == 0:
            name = _('No Purchase Taxes - Customer Taxes: ')
            for tax in at_obj.browse(cr, uid, values[1]):
                name += tax.description and tax.description or tax.name
                name += ' + '
            name = name[:-3]
        elif len(values[1]) == 0:
            name = _('Purchase Taxes: ')
            for tax in at_obj.browse(cr, uid, values[2], context=None):
                name += tax.description and tax.description or tax.name
                name += ' + '
            name = name[:-3]
            name += _('- No Customer Taxes')
        else:
            name = _('Purchase Taxes: ')
            for tax in at_obj.browse(cr, uid, values[2], context=None):
                name += tax.description and tax.description or tax.name
                name += ' + '
            name = name[:-3]
            name += _(' - Customer Taxes: ')
            for tax in at_obj.browse(cr, uid, values[1], context=None):
                name += tax.description and tax.description or tax.name
                name += ' + '
            name = name[:-3]
        name = name[:self._MAX_LENGTH_NAME] \
            if len(name) > self._MAX_LENGTH_NAME else name
        return self.create(cr, uid, {
            'name': name,
            'company_id': values[0],
            'customer_tax_ids': [(6, 0, values[1])],
            'supplier_tax_ids': [(6, 0, values[2])]}, context=context)

    def init(self, cr):
        """Generate Taxes Groups for each combinations of Taxes Group set
        in product"""
        uid = SUPERUSER_ID
        pt_obj = self.pool['product.template']
        tg_obj = self.pool['tax.group']

        # Get all Taxes Group (if update process)
        list_res = {}
        tg_ids = tg_obj.search(
            cr, uid, ['|', ('active', '=', False), ('active', '=', True)])
        tg_list = tg_obj.browse(cr, uid, tg_ids)
        for tg in tg_list:
            list_res[tg.id] = [
                tg.company_id and tg.company_id.id or False,
                sorted([x.id for x in tg.customer_tax_ids]),
                sorted([x.id for x in tg.supplier_tax_ids])]

        # Get all product template without taxes group defined
        pt_ids = pt_obj.search(cr, uid, [('tax_group_id', '=', False)])

        pt_list = pt_obj.browse(cr, uid, pt_ids)
        counter = 0
        total = len(pt_list)
        # Associate product template to existing or new taxes group
        for pt in pt_list:
            counter += 1
            res = [
                pt.company_id and pt.company_id.id or False,
                sorted([x.id for x in pt.taxes_id]),
                sorted([x.id for x in pt.supplier_taxes_id])]
            if res not in list_res.values():
                _logger.info(
                    """create new Taxes Group. Product templates"""
                    """ managed %s/%s""" % (counter, total))
                tg_id = self.find_or_create(cr, uid, res)
                list_res[tg_id] = res
                # associate product template to the new Taxes Group
                pt_obj.write(cr, uid, [pt.id], {'tax_group_id': tg_id})
            else:
                # associate product template to existing Taxes Group
                pt_obj.write(cr, uid, [pt.id], {
                    'tax_group_id': list_res.keys()[
                        list_res.values().index(res)]})
