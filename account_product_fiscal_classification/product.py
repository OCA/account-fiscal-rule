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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_fiscal_classification = fields.Many2one(
        'account.product.fiscal.classification',
        string=u"Fiscal Classification", company_dependent=True,
        help="Company wise (eg localizable) Fiscal Classification")

    @api.multi
    def fiscal_classification_id_change(self, fiscal_classification_id,
                                        sale_tax_ids, purchase_tax_ids):
        """We eventually keep the sale and purchase taxes because those
        are not company wise in OpenERP. So if we choose a different
        fiscal position for a different company, we don't want to override
        other's companies setting"""

        if not sale_tax_ids:
            sale_tax_ids = [[6, 0, []]]

        if not purchase_tax_ids:
            purchase_tax_ids = [[6, 0, []]]

        result = {'value': {}}
        if fiscal_classification_id:
            fiscal_class = self.env[
                'account.product.fiscal.classification'].browse(
                    fiscal_classification_id)
            current_company_id = self.env.user.company_id.ids
            to_keep_sale_tax = self.env['account.tax'].search(
                [('id', 'in', sale_tax_ids[0][2]),
                    ('company_id', 'not in', current_company_id)])
            to_keep_purchase_tax = self.env['account.tax'].search(
                [('id', 'in', purchase_tax_ids[0][2]),
                    ('company_id', 'not in', current_company_id)])

            result['value']['taxes_id'] = list(set(to_keep_sale_tax.ids + [
                x.id for x in fiscal_class.sale_base_tax_ids]))
            result['value']['supplier_taxes_id'] = list(
                set(to_keep_purchase_tax.ids + [
                    x.id for x in fiscal_class.purchase_base_tax_ids]))
        return result


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def fiscal_classification_id_change(self, fiscal_classification_id,
                                        sale_tax_ids, purchase_tax_ids):
        """We eventually keep the sale and purchase taxes because those
        are not company wise in OpenERP. So if we choose a different
        fiscal position for a different company, we don't want to override
        other's companies setting"""
        product_template = self.env['product.template']
        return product_template.fiscal_classification_id_change(
            fiscal_classification_id, sale_tax_ids, purchase_tax_ids)
