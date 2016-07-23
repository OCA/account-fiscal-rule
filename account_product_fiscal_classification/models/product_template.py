# -*- coding: utf-8 -*-
# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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

    # Constraint Section
    @api.multi
    @api.constrains('fiscal_classification_id', 'categ_id')
    def _check_classification_categ(self):
        for template in self:
            if template.categ_id.fiscal_restriction and\
                    template.fiscal_classification_id not in\
                    template.categ_id.fiscal_classification_ids:
                raise ValidationError(_(
                    "The category '%s' of the product '%s'"
                    " doesn't not allow to set the classification '%s'.\n"
                    " Please, change the classification of the product, or"
                    " remove the constraint on the product category.\n\n"
                    " Allowed Classifications for '%s': %s") % (
                    template.categ_id.complete_name, template.name,
                    template.fiscal_classification_id.name,
                    template.categ_id.complete_name,
                    ''.join(
                        ['\n - ' + x.name for x in
                            template.categ_id.fiscal_classification_ids])))

    # View Section
    @api.onchange('categ_id', 'fiscal_classification_id')
    def _onchange_categ_fiscal_classification_id(self):
        if self.categ_id and self.categ_id.fiscal_restriction:
            if len(self.categ_id.fiscal_classification_ids) == 1:
                # Set classification if category allows only one
                self.fiscal_classification_id =\
                    self.categ_id.fiscal_classification_ids[0]
            elif self.fiscal_classification_id not in\
                    self.categ_id.fiscal_classification_ids:
                # Remove classification if category and classification are not
                # compatible
                self.fiscal_classification_id = None

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

    # Custom Section
    @api.multi
    def write_taxes_setting(self, vals):
        """If Fiscal Classification is defined, set the according taxes
        to the product(s); Otherwise, find the correct Fiscal classification,
        depending of the taxes, or create a new one, if no one are found."""
        for template in self:
            if vals.get('fiscal_classification_id', False):
                # update or replace 'taxes_id' and 'supplier_taxes_id'
                classification = template.fiscal_classification_id
                tax_vals = {
                    'supplier_taxes_id': [[6, 0, [
                        x.id for x in classification.purchase_tax_ids]]],
                    'taxes_id': [[6, 0, [
                        x.id for x in classification.sale_tax_ids]]],
                    }
                super(ProductTemplate, template.sudo()).write(tax_vals)
            elif ('supplier_taxes_id' in vals.keys() or
                    'taxes_id' in vals.keys()):
                # product template Single update mode
                fc_obj = self.env['account.product.fiscal.classification']
                if len(self) != 1:
                    raise ValidationError(
                        _("You cannot change Taxes for many Products."))
                purchase_tax_ids = [
                    x.id for x in template.sudo().supplier_taxes_id]
                sale_tax_ids = [
                    x.id for x in template.sudo().taxes_id]
                fc_id = fc_obj.find_or_create(
                    template.company_id.id, sale_tax_ids, purchase_tax_ids)
                super(ProductTemplate, template.sudo()).write(
                    {'fiscal_classification_id': fc_id})
