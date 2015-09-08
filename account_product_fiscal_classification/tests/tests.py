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

from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class Tests(TransactionCase):
    """Tests for 'Account Product - Fiscal Classification' Module"""

    def setUp(self):
        super(Tests, self).setUp()
        self.pt_obj = self.env['product.template']
        self.tg_obj = self.env['tax.group']
        self.wizard_obj = self.env['wizard.change.tax.group']
        self.main_company_id = self.ref('base.main_company')
        self.tg1_id = self.ref('product_taxes_group.tax_group_1')
        self.tg2_id = self.ref('product_taxes_group.tax_group_2')
        self.pt1_id = self.ref('product_taxes_group.product_template_1')
        self.at_purchase_1_id = self.ref(
            'product_taxes_group.account_tax_purchase_1')
        self.at_sale_1_id = self.ref('product_taxes_group.account_tax_sale_1')
        self.at_sale_2_id = self.ref('product_taxes_group.account_tax_sale_2')

    # Test Section
    def test_01_change_group(self):
        """Test the behaviour when we change Taxes Group for products."""
        wizard = self.wizard_obj.create({
            'old_tax_group_id': self.tg1_id, 'new_tax_group_id': self.tg2_id})
        wizard.button_change_tax_group()
        pt = self.pt_obj.browse(self.pt1_id)
        self.assertEqual(
            pt.tax_group_id.id, self.tg2_id,
            "Taxes Group change has failed for products via Wizard.")

    def test_02_check_coherent_vals_tax_group_exist(self):
        """Test the behaviour of the function product.template
        check_coherent_vals() when the combination exist."""
        # Set tax_group_1 configuration to the product
        vals = {
            'name': 'Product Product Name',
            'company_id': self.main_company_id,
            'supplier_taxes_id': [[6, 0, [self.at_purchase_1_id]]],
            'taxes_id': [[6, 0, [self.at_sale_1_id, self.at_sale_2_id]]],
        }
        pt = self.pt_obj.create(vals)
        self.assertEqual(
            pt.tax_group_id.id, self.tg1_id,
            "Recovery of Correct Taxes Group failed during creation.")
        # Set tax_group_2 configuration to the product
        vals = {
            'supplier_taxes_id': [[6, 0, []]],
            'taxes_id': [[6, 0, [self.at_sale_2_id]]],
        }
        pt.write(vals)
        self.assertEqual(
            pt.tax_group_id.id, self.tg2_id,
            "Recovery of Correct Taxes Group failed during update.")

    def test_03_check_coherent_vals_tax_group_doesnt_exist_single(self):
        """Test the behaviour of the function product.template
        check_coherent_vals() when the combination doesn't exist.
        (Single Tax)"""
        vals = {
            'name': 'Product Product Name',
            'company_id': self.main_company_id,
            'supplier_taxes_id': [[6, 0, [self.at_purchase_1_id]]],
            'taxes_id': [[6, 0, [self.at_sale_1_id]]],
        }
        count_before = self.tg_obj.search_count([])
        self.pt_obj.create(vals)
        count_after = self.tg_obj.search_count([])
        self.assertEqual(
            count_before + 1, count_after,
            "New combination must create new Taxes Group.")

    def test_04_check_coherent_vals_tax_group_doesnt_exist_multi(self):
        """Test the behaviour of the function product.template
        check_coherent_vals() when the combination doesn't exist.
        (Multiple Taxes)"""
        vals = {
            'name': 'Product Product Name',
            'company_id': self.main_company_id,
            'supplier_taxes_id': [[6, False, []]],
            'taxes_id': [[6, False, [self.at_sale_1_id, self.at_sale_2_id]]],
        }
        count_before = self.tg_obj.search_count([])
        self.pt_obj.create(vals)
        count_after = self.tg_obj.search_count([])
        self.assertEqual(
            count_before + 1, count_after,
            "New combination must create new Taxes Group.")

    def test_05_update_tax_group(self):
        """Test if changing a Taxes Group Configuration change the product."""
        tg = self.tg_obj.browse([self.tg1_id])
        tg.write({'customer_tax_ids': [[6, 0, [self.at_sale_1_id]]]})
        pt = self.pt_obj.browse([self.pt1_id])[0]
        self.assertEqual(
            [
                [x.id for x in pt.taxes_id],
                [x.id for x in pt.supplier_taxes_id]],
            [[self.at_sale_1_id], [self.at_purchase_1_id]],
            "Update taxes in Taxes Group must update associated Products.")

    def test_06_unlink_tax_group(self):
        """Test if unlinking a Taxes Group with products fails."""
        tg = self.tg_obj.browse([self.tg1_id])
        with self.assertRaises(ValidationError):
            tg.unlink()
