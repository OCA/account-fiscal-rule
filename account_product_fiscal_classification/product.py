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


class product_template(osv.Model):
    _inherit = 'product.template'
    _columns = {
        'property_fiscal_classification': fields.property(
            'account.product.fiscal.classification',
            type='many2one',
            relation='account.product.fiscal.classification',
            string="Fiscal Classification",
            view_load=True,
            help="Company wise (eg localizable) Fiscal Classification"),
    }

    def fiscal_classification_id_change(self, cr, uid, ids,
                                        fiscal_classification_id=False,
                                        sale_tax_ids=None,
                                        purchase_tax_ids=None, context=None):
        """We eventually keep the sale and purchase taxes because those
        are not company wise in OpenERP. So if we choose a different
        fiscal position for a different company, we don't want to override
        other's companies setting"""

        if not context:
            context = {}

        if not sale_tax_ids:
            sale_tax_ids = [[6, 0, []]]

        if not purchase_tax_ids:
            purchase_tax_ids = [[6, 0, []]]

        result = {'value': {}}
        if fiscal_classification_id:
            fclass = self.pool.get('account.product.fiscal.classification')
            fiscal_classification = fclass.browse(
                cr, uid, fiscal_classification_id, context=context)

            current_company_id = self.pool.get('res.users').browse(
                cr, uid, uid).company_id.id
            to_keep_sale_tax_ids = self.pool.get('account.tax').search(
                cr, uid, [('id', 'in', sale_tax_ids[0][2]),
                    ('company_id', '!=', current_company_id)],
                        context=context)
            to_keep_purchase_tax_ids = self.pool.get('account.tax').search(
                cr, uid, [('id', 'in', purchase_tax_ids[0][2]),
                    ('company_id', '!=', current_company_id)],
                        context=context)

            result['value']['taxes_id'] = list(set(to_keep_sale_tax_ids + [x.id for x in fiscal_classification.sale_base_tax_ids]))
            result['value']['supplier_taxes_id'] = list(set(to_keep_purchase_tax_ids + [x.id for x in fiscal_classification.purchase_base_tax_ids]))
        return result


class product_product(osv.Model):
    _inherit = "product.product"

    def fiscal_classification_id_change(self, cr, uid, ids,
                                        fiscal_classification_id=False,
                                        sale_tax_ids=None,
                                        purchase_tax_ids=None, context=None):
        """We eventually keep the sale and purchase taxes because those
        are not company wise in OpenERP. So if we choose a different
        fiscal position for a different company, we don't want to override
        other's companies setting"""

        product_template = self.pool.get('product.template')
        return product_template.fiscal_classification_id_change(
            cr, uid, ids, fiscal_classification_id, sale_tax_ids,
            purchase_tax_ids)
