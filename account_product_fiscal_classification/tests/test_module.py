# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProductTemplate = self.env["product.template"]
        self.ResCompany = self.env["res.company"]
        self.FiscalClassification = self.env["account.product.fiscal.classification"]
        self.WizardChange = self.env["wizard.change.fiscal.classification"]

        self.main_company = self.env.ref("base.main_company")
        self.group_accountant = self.env.ref("account.group_account_manager")
        self.group_system = self.env.ref("base.group_system")
        self.company_2 = self.env.ref("account_product_fiscal_classification.company_2")
        self.user_demo = self.env.ref("base.user_demo")

        self.fiscal_classification_A_company_1 = self.env.ref(
            "account_product_fiscal_classification.fiscal_classification_A_company_1"
        )
        self.fiscal_classification_B_company_1 = self.env.ref(
            "account_product_fiscal_classification.fiscal_classification_B_company_1"
        )
        self.fiscal_classification_D_global = self.env.ref(
            "account_product_fiscal_classification.fiscal_classification_D_global"
        )
        self.product_template_A_company_1 = self.env.ref(
            "account_product_fiscal_classification.product_template_A_company_1"
        )
        self.account_tax_purchase_20_company_1 = self.env.ref(
            "account_product_fiscal_classification.account_tax_purchase_20_company_1"
        )
        self.account_tax_sale_20_company_1 = self.env.ref(
            "account_product_fiscal_classification.account_tax_sale_20_company_1"
        )
        self.account_tax_purchase_7_company_2 = self.env.ref(
            "account_product_fiscal_classification.account_tax_purchase_7_company_2"
        )
        self.chart_template = self.env.ref(
            "account_product_fiscal_classification.chart_template"
        )
        # self.sale_tax_2 = self.env.ref(
        #     "account_product_fiscal_classification.account_tax_sale_5_company_1"
        # )

        self.category_all = self.env.ref("product.product_category_all")
        self.category_wine = self.env.ref(
            "account_product_fiscal_classification.category_wine"
        )

        # # Group to create product
        # self.product_group = self.env.ref("account.group_account_manager")
        # self.restricted_group = self.env.ref("base.group_system")

    # Test Section
    def test_01_change_classification(self):
        """Test the behaviour when we change Fiscal Classification for
        products."""
        wizard = self.WizardChange.create(
            {
                "old_fiscal_classification_id": self.fiscal_classification_A_company_1.id,
                "new_fiscal_classification_id": self.fiscal_classification_B_company_1.id,
            }
        )
        wizard.button_change_fiscal_classification()
        self.assertEqual(
            self.product_template_A_company_1.fiscal_classification_id,
            self.fiscal_classification_B_company_1,
            "Fiscal Classification change has failed for products via Wizard.",
        )

    def test_02_create_product(self):
        """Test if creating a product with fiscal classification set correct taxes"""
        vals = {
            "name": "Product Product Name",
            "company_id": self.main_company.id,
            "fiscal_classification_id": self.fiscal_classification_D_global.id,
        }
        newTemplate = self.ProductTemplate.create(vals)
        # Test that all taxes are set (in sudo mode)
        self.assertEqual(
            set(newTemplate.sudo().taxes_id.ids),
            set(self.fiscal_classification_D_global.sudo().sale_tax_ids.ids),
        )
        self.assertEqual(
            set(newTemplate.sudo().supplier_taxes_id.ids),
            set(self.fiscal_classification_D_global.sudo().purchase_tax_ids.ids),
        )

    def test_03_update_fiscal_classification(self):
        """Test if changing a Configuration of a Fiscal Classification changes
        the product."""
        self.fiscal_classification_A_company_1.write(
            {"sale_tax_ids": [(6, 0, [self.account_tax_sale_20_company_1.id])]}
        )
        self.assertEqual(
            set(self.product_template_A_company_1.taxes_id.ids),
            {self.account_tax_sale_20_company_1.id},
            "Update taxes in Fiscal Classification must update associated " "Products.",
        )

    def test_05_unlink_fiscal_classification(self):
        """Test if unlinking a Fiscal Classification with products fails."""
        with self.assertRaises(ValidationError):
            self.fiscal_classification_A_company_1.unlink()

    def test_10_chart_template(self):
        """Test if installing new CoA creates correct classification"""
        new_company = self.ResCompany.create({"name": "New Company"})
        self.chart_template.try_loading(company=new_company, install_demo=False)
        new_classifications = self.FiscalClassification.search(
            [("company_id", "=", new_company.id)]
        )
        self.assertEqual(len(new_classifications), 1)
        self.assertEqual(len(new_classifications[0].purchase_tax_ids), 1)
        self.assertEqual(
            new_classifications[0].purchase_tax_ids[0].name,
            "Demo Purchase Tax Template 20%",
        )

    def test_20_hook(self):
        vals = self.FiscalClassification._prepare_vals_from_taxes(
            self.account_tax_purchase_20_company_1,
            self.account_tax_sale_20_company_1,
        )
        self.assertEqual(vals["company_id"], self.main_company.id)

        vals = self.FiscalClassification._prepare_vals_from_taxes(
            self.account_tax_purchase_20_company_1
            | self.account_tax_purchase_7_company_2,
            self.account_tax_sale_20_company_1,
        )
        self.assertEqual(vals["company_id"], False)

    def test_30_rules(self):
        # Ensure that demo and admin user can create products
        self.group_system.write(
            {"users": [(6, 0, [self.env.user.id, self.user_demo.id])]}
        )

        # set only admin user as accountant
        self.group_accountant.write({"users": [(6, 0, [self.env.user.id])]})

        # Create a product without rules should success
        self._create_product(
            self.env.user, self.category_all, self.fiscal_classification_B_company_1
        )
        self._create_product(
            self.user_demo, self.category_all, self.fiscal_classification_B_company_1
        )

        # create a product not respecting rules should succeed with accountant perfil
        self._create_product(
            self.env.user, self.category_wine, self.fiscal_classification_B_company_1
        )

        # create a product not respecting rules should fail without accountant perfil
        with self.assertRaises(ValidationError):
            self._create_product(
                self.user_demo,
                self.category_wine,
                self.fiscal_classification_B_company_1,
            )

    def _create_product(self, user, category, classification):
        vals = {
            "name": "Test Product",
            "categ_id": category.id,
            "fiscal_classification_id": classification.id,
        }
        self.ProductTemplate.with_user(user).create(vals)
