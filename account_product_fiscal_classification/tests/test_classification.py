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

from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class Tests(TransactionCase):
    """Tests for 'Account Product - Fiscal Classification' Module"""

    def setUp(self):
        super(Tests, self).setUp()
        self.template_obj = self.env['product.template']
        self.classification_template_obj =\
            self.env['account.product.fiscal.classification.template']
        self.classification_obj =\
            self.env['account.product.fiscal.classification']
        self.wizard_template_obj =\
            self.env['wizard.account.product.fiscal.classification']
        self.wizard_obj = self.env['wizard.change.fiscal.classification']
        self.main_company_id = self.ref('base.main_company')
        self.classification_template_1_id = self.ref(
            'account_product_fiscal_classification.fiscal_classification'
            '_template_1')
        self.classification_1_id = self.ref(
            'account_product_fiscal_classification.fiscal_classification_1')
        self.classification_2_id = self.ref(
            'account_product_fiscal_classification.fiscal_classification_2')
        self.template_id = self.ref(
            'account_product_fiscal_classification.product_template_1')
        self.purchase_tax_id = self.ref(
            'account_product_fiscal_classification.account_tax_purchase_1')
        self.sale_tax_1_id = self.ref(
            'account_product_fiscal_classification.account_tax_sale_1')
        self.sale_tax_2_id = self.ref(
            'account_product_fiscal_classification.account_tax_sale_2')

    # Test Section
    def test_01_change_classification(self):
        """Test the behaviour when we change Fiscal Classification for
        products."""
        wizard = self.wizard_obj.create({
            'old_fiscal_classification_id': self.classification_1_id,
            'new_fiscal_classification_id': self.classification_2_id})
        wizard.button_change_fiscal_classification()
        template = self.template_obj.browse(self.template_id)
        self.assertEqual(
            template.fiscal_classification_id.id, self.classification_2_id,
            "Fiscal Classification change has failed for products via Wizard.")

    def test_02_write_taxes_setting_classification_exist(self):
        """Test the behaviour of the function product.template
        write_taxes_setting() when the combination of taxes exist."""
        # Set classification_1 configuration to the product
        vals = {
            'name': 'Product Product Name',
            'company_id': self.main_company_id,
            'supplier_taxes_id': [[6, 0, [self.purchase_tax_id]]],
            'taxes_id': [[6, 0, [self.sale_tax_1_id, self.sale_tax_2_id]]],
        }
        template = self.template_obj.create(vals)
        self.assertEqual(
            template.fiscal_classification_id.id, self.classification_1_id,
            "Recovery of Correct Taxes Group failed during creation.")
        # Set classification_2 configuration to the product
        vals = {
            'supplier_taxes_id': [[6, 0, []]],
            'taxes_id': [[6, 0, [self.sale_tax_2_id]]],
        }
        template.write(vals)
        self.assertEqual(
            template.fiscal_classification_id.id, self.classification_2_id,
            "Recovery of Correct Taxes Group failed during update.")

    def test_03_write_taxes_setting_classification_doesnt_exist_single(self):
        """Test the behaviour of the function product.template
        write_taxes_setting() when the combination doesn't exist.
        (Single Tax)"""
        vals = {
            'name': 'Product Product Name',
            'company_id': self.main_company_id,
            'supplier_taxes_id': [[6, 0, [self.purchase_tax_id]]],
            'taxes_id': [[6, 0, [self.sale_tax_1_id]]],
        }
        count_before = self.classification_obj.search_count([])
        self.template_obj.create(vals)
        count_after = self.classification_obj.search_count([])
        self.assertEqual(
            count_before + 1, count_after,
            "New combination must create new Fiscal Classification.")

    def test_04_write_taxes_setting_classification_doesnt_exist_multi(self):
        """Test the behaviour of the function product.template
        write_taxes_setting() when the combination doesn't exist.
        (Multiple Taxes)"""
        vals = {
            'name': 'Product Product Name',
            'company_id': self.main_company_id,
            'supplier_taxes_id': [[6, False, []]],
            'taxes_id': [[6, False, [self.sale_tax_1_id, self.sale_tax_2_id]]],
        }
        count_before = self.classification_obj.search_count([])
        self.template_obj.create(vals)
        count_after = self.classification_obj.search_count([])
        self.assertEqual(
            count_before + 1, count_after,
            "New combination must create new Fiscal Classification.")

    def test_05_update_fiscal_classification(self):
        """Test if changing a Configuration of a Fiscal Classificationchange
            the product."""
        tg = self.classification_obj.browse([self.classification_1_id])
        tg.write({'sale_tax_ids': [[6, 0, [self.sale_tax_1_id]]]})
        template = self.template_obj.browse([self.template_id])[0]
        self.assertEqual(
            [
                [x.id for x in template.taxes_id],
                [x.id for x in template.supplier_taxes_id]
            ],
            [
                [self.sale_tax_1_id], [self.purchase_tax_id]
            ],
            ("Update taxes in Fiscal Classification must update associated "
             "Products."))

    def test_06_unlink_fiscal_classification(self):
        """Test if unlinking a Fiscal Classification with products fails."""
        classification = self.classification_obj.browse(
            [self.classification_1_id])
        with self.assertRaises(ValidationError):
            classification.unlink()

    def test_07_classification_generate_from_template(self):
        """Test wizard generate fiscal classification from template."""
        wizard_template = self.wizard_template_obj.create({})
        wizard_template.action_create()
        template = self.classification_template_obj.browse(
            self.classification_template_1_id)
        self.assertTrue(self.classification_obj.search(
            [('code', '=', template.code)]))
