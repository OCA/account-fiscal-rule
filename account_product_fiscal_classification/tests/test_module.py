# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    def setUp(self):
        super(Tests, self).setUp()
        self.ProductTemplate = self.env["product.template"]
        self.FiscalClassification = self.env["account.product.fiscal.classification"]
        self.WizardChange = self.env["wizard.change.fiscal.classification"]

        self.main_company = self.env.ref("base.main_company")
        self.user_demo = self.env.ref("base.user_demo")

        self.classification_1 = self.env.ref(
            "account_product_fiscal_classification.fiscal_classification_1"
        )
        self.classification_2 = self.env.ref(
            "account_product_fiscal_classification.fiscal_classification_2"
        )
        self.product_template = self.env.ref(
            "account_product_fiscal_classification.product_template_1"
        )
        self.purchase_tax = self.env.ref(
            "account_product_fiscal_classification.account_tax_purchase_1"
        )
        self.sale_tax_1 = self.env.ref(
            "account_product_fiscal_classification.account_tax_sale_1"
        )
        self.sale_tax_2 = self.env.ref(
            "account_product_fiscal_classification.account_tax_sale_2"
        )

        self.product_category = self.env.ref("product.product_category_all")

        # Group to create product
        self.product_group = self.env.ref("account.group_account_manager")
        self.restricted_group = self.env.ref("base.group_system")

    # Test Section
    def test_01_change_classification(self):
        """Test the behaviour when we change Fiscal Classification for
        products."""
        wizard = self.WizardChange.create(
            {
                "old_fiscal_classification_id": self.classification_1.id,
                "new_fiscal_classification_id": self.classification_2.id,
            }
        )
        wizard.button_change_fiscal_classification()
        self.assertEqual(
            self.product_template.fiscal_classification_id,
            self.classification_2,
            "Fiscal Classification change has failed for products via Wizard.",
        )

    def test_02_write_taxes_setting_classification_exist(self):
        """Test the behaviour of the function product.template
        write_taxes_setting() when the combination of taxes exist."""
        # Set classification_1 configuration to the product
        vals = {
            "name": "Product Product Name",
            "company_id": self.main_company.id,
            "supplier_taxes_id": [(6, 0, [self.purchase_tax.id])],
            "taxes_id": [(6, 0, [self.sale_tax_1.id, self.sale_tax_2.id])],
        }
        newTemplate = self.ProductTemplate.create(vals)
        self.assertEqual(
            newTemplate.fiscal_classification_id,
            self.classification_1,
            "Recovery of Correct Taxes Group failed during creation.",
        )

        # Set classification_2 configuration to the product
        vals = {
            "supplier_taxes_id": [(6, 0, [])],
            "taxes_id": [(6, 0, [self.sale_tax_2.id])],
        }
        newTemplate.write(vals)
        self.assertEqual(
            newTemplate.fiscal_classification_id,
            self.classification_2,
            "Recovery of Correct Taxes Group failed during update.",
        )

    def test_03_write_taxes_setting_classification_doesnt_exist_single(self):
        """Test the behaviour of the function product.template
        write_taxes_setting() when the combination doesn't exist.
        (Single Tax)"""
        vals = {
            "name": "Product Product Name",
            "company_id": self.main_company.id,
            "supplier_taxes_id": [(6, 0, [self.purchase_tax.id])],
            "taxes_id": [(6, 0, [self.sale_tax_1.id])],
        }
        count_before = self.FiscalClassification.search_count([])
        self.ProductTemplate.create(vals)
        count_after = self.FiscalClassification.search_count([])
        self.assertEqual(
            count_before + 1,
            count_after,
            "New combination must create new Fiscal Classification.",
        )

    def test_04_write_taxes_setting_classification_doesnt_exist_multi(self):
        """Test the behaviour of the function product.template
        write_taxes_setting() when the combination doesn't exist.
        (Multiple Taxes)"""
        vals = {
            "name": "Product Product Name",
            "company_id": self.main_company.id,
            "supplier_taxes_id": [(6, False, [])],
            "taxes_id": [(6, False, [self.sale_tax_1.id, self.sale_tax_2.id])],
        }
        count_before = self.FiscalClassification.search_count([])
        self.ProductTemplate.create(vals)
        count_after = self.FiscalClassification.search_count([])
        self.assertEqual(
            count_before + 1,
            count_after,
            "New combination must create new Fiscal Classification.",
        )

    def test_05_update_fiscal_classification(self):
        """Test if changing a Configuration of a Fiscal Classification changes
        the product."""
        self.classification_1.write({"sale_tax_ids": [(6, 0, [self.sale_tax_1.id])]})
        self.assertEqual(
            [
                {x.id for x in self.product_template.taxes_id},
                {x.id for x in self.product_template.supplier_taxes_id},
            ],
            [{self.sale_tax_1.id}, {self.purchase_tax.id}],
            (
                "Update taxes in Fiscal Classification must update associated "
                "Products."
            ),
        )

    def test_06_unlink_fiscal_classification(self):
        """Test if unlinking a Fiscal Classification with products fails."""
        with self.assertRaises(ValidationError):
            self.classification_1.unlink()

    def test_07_access_restriction_fiscal_classification(self):
        # Give access to user to create product
        self.product_group.users = [(4, self.user_demo.id, 0)]
        # Create a product should success w/o classification
        self._create_product(self.user_demo, False)
        self._create_product(self.user_demo, True)

        # Restrict access to the classification
        self.classification_1.usage_group_id = self.restricted_group
        # Create a product should success without classification
        # and should fail with classification
        self._create_product(self.user_demo, False)
        with self.assertRaises(UserError):
            self._create_product(self.user_demo, True)

        # Give access to the user
        self.restricted_group.users = [(4, self.user_demo.id, 0)]
        # Create a product should success with classification
        self._create_product(self.user_demo, True)

    def _create_product(self, user, with_classification):
        vals = {
            "name": "Demo Product",
            "categ_id": self.product_category.id,
        }
        if with_classification:
            vals.update({"fiscal_classification_id": self.classification_1.id})
        self.ProductTemplate.with_user(user).create(vals)
