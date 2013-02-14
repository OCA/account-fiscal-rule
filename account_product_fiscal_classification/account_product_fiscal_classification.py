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

from osv import fields, osv


class account_product_fiscal_classification(osv.Model):
    _name = 'account.product.fiscal.classification'
    _description = 'Product Fiscal Classification'
    _columns = {
                'name': fields.char('Main code', size=32, required=True),
                'description': fields.char('Description', size=64),
                'company_id': fields.many2one('res.company', 'Company'),
                 # TODO restrict to company_id if company_id set when
                 # framework will allow it:
                'sale_base_tax_ids': fields.many2many(
                    'account.tax', 'fiscal_classification_sale_tax_rel',
                    'fiscal_classification_id', 'tax_id', 'Base Sale Taxes',
                    domain=[('type_tax_use', '!=', 'purchase')]),
                'purchase_base_tax_ids': fields.many2many(
                    'account.tax', 'fiscal_classification_purchase_tax_rel',
                    'fiscal_classification_id', 'tax_id',
                    'Base Purchase Taxes',
                    domain=[('type_tax_use', '!=', 'sale')])
    }

    def button_update_products(self, cr, uid, ids, context=None):

        result = True
        if not context:
            context = {}

        obj_product = self.pool.get('product.template')

        for fiscal_classification in self.browse(cr, uid, ids):
            property_ids = self.pool.get('ir.property').search(
                cr, uid,
                [('name', '=', 'property_fiscal_classification'),
                ('res_id', 'ilike', 'product.template,'),
                ('value_reference', '=', 'account.product.fiscal.classification,%s' % fiscal_classification.id)])

            reads = self.pool.get('ir.property').read(
                cr, uid, property_ids, ['res_id'])
            product_ids = [int(l['res_id'].split(',')[1]) for l in reads]
            current_company_id = self.pool.get('res.users').browse(
                cr, uid, uid).company_id.id

            for product in obj_product.browse(cr, uid, product_ids, context):
                to_keep_sale_tax_ids = self.pool.get('account.tax').search(
                    cr, uid, [('id', 'in', [x.id for x in product.taxes_id]),
                              ('company_id', '!=', current_company_id)])

                to_keep_purchase_tax_ids = self.pool.get('account.tax').search(
                    cr, uid, [('id', 'in', [x.id for x in product.supplier_taxes_id]),
                    ('company_id', '!=', current_company_id)])

                vals = {
                        'taxes_id': [(6, 0, list(set(to_keep_sale_tax_ids + [x.id for x in fiscal_classification.sale_base_tax_ids])))],
                        'supplier_taxes_id': [(6, 0, list(set(to_keep_purchase_tax_ids + [x.id for x in fiscal_classification.purchase_base_tax_ids])))],
                }

                obj_product.write(cr, uid, product.id, vals, context)

        return result

    def name_search(self, cr, user, name='', args=None, operator='ilike',
                    context=None, limit=80):

        if not args:
            args = []

        if not context:
            context = {}

        if name:
            ids = self.search(cr, user, [('name', '=', name)] + args,
                              limit=limit, context=context)
            if not len(ids):
                ids = self.search(
                    cr, user, [('description', '=', name)] + args,
                    limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('name', operator, name)] + args,
                                  limit=limit, context=context)
                ids += self.search(
                    cr, user, [('description', operator, name)] + args,
                    limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)

        return self.name_get(cr, user, ids, context)


class account_product_fiscal_classification_template(osv.Model):
    _name = 'account.product.fiscal.classification.template'
    _description = 'Product Fiscal Classification Template'
    _columns = {
                'name': fields.char('Main code', size=32, required=True),
                'description': fields.char('Description', size=64),
                # TODO restrict to company_id if company_id set when
                # framework will allow it:
                'sale_base_tax_ids': fields.many2many(
                    'account.tax.template',
                    'fiscal_classification_template_sale_tax_rel',
                    'fiscal_classification_id', 'tax_id',
                    'Base Sale Taxes',
                    domain=[('type_tax_use', '!=', 'purchase')]),
                'purchase_base_tax_ids': fields.many2many(
                    'account.tax.template',
                    'fiscal_classification_template_purchase_tax_rel',
                    'fiscal_classification_id',
                    'tax_id', 'Base Purchase Taxes',
                    domain=[('type_tax_use', '!=', 'sale')]),
    }

    def name_search(self, cr, user, name='', args=None, operator='ilike',
                    context=None, limit=80):

        if not args:
            args = []

        if not context:
            context = {}

        if name:
            ids = self.search(cr, user, [('name', '=', name)] + args,
                              limit=limit, context=context)
            if not len(ids):
                ids = self.search(
                    cr, user, [('description', '=', name)] + args,
                    limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('name', operator, name)] + args,
                                  limit=limit, context=context)
                ids += self.search(
                    cr, user, [('description', operator, name)] + args,
                    limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)

        return self.name_get(cr, user, ids, context)


class wizard_account_product_fiscal_classification(osv.TransientModel):
    _name = 'wizard.account.product.fiscal.classification'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c:
            self.pool.get('res.users').browse(
                cr, uid, [uid], c)[0].company_id.id,
    }

    def action_create(self, cr, uid, ids, context=None):
        obj_wizard = self.browse(cr, uid, ids[0])
        obj_tax = self.pool.get('account.tax')
        obj_tax_template = self.pool.get('account.tax.template')
        obj_fc = self.pool.get('account.product.fiscal.classification')
        obj_fc_template = self.pool.get(
            'account.product.fiscal.classification.template')

        company_id = obj_wizard.company_id.id
        tax_template_ref = {}

        tax_ids = obj_tax.search(
            cr, uid, [('company_id', '=', company_id)], context=context)

        for tax in obj_tax.browse(cr, uid, tax_ids, context=context):
            tax_template = obj_tax_template.search(
                cr, uid, [('name', '=', tax.name)], context=context)[0]

            if tax_template:
                tax_template_ref[tax_template] = tax.id

        fclass_ids_template = obj_fc_template.search(
            cr, uid, [], context=context)

        for fclass_template in obj_fc_template.browse(
            cr, uid, fclass_ids_template, context=context):

            fclass_id = obj_fc.search(
                cr, uid, [('name', '=', fclass_template.name)],
                context=context)

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
                obj_fc.create(cr, uid, vals, context)

        return {}
