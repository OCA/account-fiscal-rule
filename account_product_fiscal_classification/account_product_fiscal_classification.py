# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_product_fiscal_classification for OpenERP
#   Copyright (C) 2010-TODAY Akretion <http://www.akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
#     @author Raphaël Valyi <rvalyi@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api


class AccountProductFiscalClassification(models.Model):
    _name = 'account.product.fiscal.classification'
    _description = 'Product Fiscal Classification'

    name = fields.Char('Main code', size=32, required=True)
    description = fields.Char('Description', size=64)
    company_id = fields.Many2one('res.company', 'Company')
    # TODO restrict to company_id if company_id set when
    # framework will allow it:
    sale_base_tax_ids = fields.Many2many(
        'account.tax', 'fiscal_classification_sale_tax_rel',
        'fiscal_classification_id', 'tax_id', 'Base Sale Taxes',
        domain=[('type_tax_use', '!=', 'purchase')])
    purchase_base_tax_ids = fields.Many2many(
        'account.tax', 'fiscal_classification_purchase_tax_rel',
        'fiscal_classification_id', 'tax_id',
        'Base Purchase Taxes', domain=[('type_tax_use', '!=', 'sale')])

    @api.multi
    def button_update_products(self):

        result = True

        for fiscal_class in self:
            property_search = self.env['ir.property'].search([
                ('name', '=', 'property_fiscal_classification'),
                ('res_id', 'ilike', 'product.template,'),
                ('value_reference', '=',
                 'account.product.fiscal.classification,%s' %
                 fiscal_class.id)])

            product_ids = [
                int(l.res_id.split(',')[1]) for l in property_search]
            current_company_id = self.env.user.company_id.id

            for product in self.env['product.template'].browse(product_ids):
                keep_sale_tax = self.env['account.tax'].search(
                    [('id', 'in', [x.id for x in product.taxes_id]),
                     ('company_id', '!=', current_company_id)])

                keep_purchase_tax = self.env['account.tax'].search(
                    [('id', 'in', [x.id for x in product.supplier_taxes_id]),
                     ('company_id', '!=', current_company_id)])

                vals = {
                    'taxes_id': [(6, 0, list(set(keep_sale_tax.ids + [
                        x.id for x in fiscal_class.sale_base_tax_ids])))],
                    'supplier_taxes_id': [(6, 0, list(set(
                        keep_purchase_tax.ids + [
                            x.id for x in
                            fiscal_class.purchase_base_tax_ids])))],
                }

                product.write(vals)

        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('name', '=', name)] + args, limit=limit)
            if not recs:
                recs = self.search([('description', '=', name)] + args,
                                   limit=limit)
            if not recs:
                recs = self.search([('name', operator, name)] + args,
                                   limit=limit)
                recs += self.search([('description', operator, name)] + args,
                                    limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args,
                               limit=limit)
        return recs.name_get()


class AccountProductFiscalClassificationTemplate(models.Model):
    _name = 'account.product.fiscal.classification.template'
    _description = 'Product Fiscal Classification Template'

    name = fields.Char('Main code', size=32, required=True)
    description = fields.Char('Description', size=64)
    # TODO restrict to company_id if company_id set when
    # framework will allow it:
    sale_base_tax_ids = fields.Many2many(
        'account.tax.template',
        'fiscal_classification_template_sale_tax_rel',
        'fiscal_classification_id', 'tax_id', 'Base Sale Taxes',
        domain=[('type_tax_use', '!=', 'purchase')])
    purchase_base_tax_ids = fields.Many2many(
        'account.tax.template',
        'fiscal_classification_template_purchase_tax_rel',
        'fiscal_classification_id', 'tax_id', 'Base Purchase Taxes',
        domain=[('type_tax_use', '!=', 'sale')])

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('name', '=', name)] + args, limit=limit)
            if not recs:
                recs = self.search([('description', '=', name)] + args,
                                   limit=limit)
            if not recs:
                recs = self.search([('name', operator, name)] + args,
                                   limit=limit)
                recs += self.search([('description', operator, name)] + args,
                                    limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args,
                               limit=limit)
        return recs.name_get()


class WizardAccountProductFiscalClassification(models.TransientModel):
    _name = 'wizard.account.product.fiscal.classification'

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'account.invoice'))

    @api.multi
    def action_create(self):
        obj_tax = self.env['account.tax']
        obj_tax_template = self.env['account.tax.template']
        obj_fc = self.env['account.product.fiscal.classification']
        obj_fc_template = self.env[
            'account.product.fiscal.classification.template']

        company_id = self.company_id.id
        tax_template_ref = {}

        for tax in obj_tax.search([('company_id', '=', company_id)]):
            tax_template = obj_tax_template.search([('name', '=', tax.name)])

            if tax_template:
                tax_template_ref[tax_template[0].id] = tax.id

        for fclass_template in obj_fc_template.search([]):

            fclass_id = obj_fc.search([('name', '=', fclass_template.name)])

            if not fclass_id:
                sale_tax_ids = []
                for tax in fclass_template.sale_base_tax_ids:
                    sale_tax_ids.append(tax_template_ref[tax.id])

                purchase_tax_ids = []
                for tax in fclass_template.purchase_base_tax_ids:
                    purchase_tax_ids.append(tax_template_ref[tax.id])

                vals = {
                    'name': fclass_template.name,
                    'description': fclass_template.description,
                    'company_id': company_id,
                    'sale_base_tax_ids': [(6, 0, sale_tax_ids)],
                    'purchase_base_tax_ids': [(6, 0, purchase_tax_ids)]
                }
                obj_fc.create(vals)

        return True
