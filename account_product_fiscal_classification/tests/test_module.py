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

        self.classification_A_company_1 = self.env.ref(
            "account_product_fiscal_classification.fiscal_classification_A_company_1"
        )
        self.classification_B_company_1 = self.env.ref(
            "account_product_fiscal_classification.fiscal_classification_B_company_1"
        )
        self.classification_D_global = self.env.ref(
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
        self.category_all = self.env.ref("product.product_category_all")
        self.category_wine = self.env.ref(
            "account_product_fiscal_classification.category_wine"
        )

        self.initial_classif_count = self.FiscalClassification.search_count([])

    def _create_product(self, extra_vals, user=False):
        if not user:
            user = self.env.user
        vals = {
            "name": "Test Product",
            "company_id": self.main_company.id,
            "categ_id": self.category_all.id,
        }
        vals.update(extra_vals)
        return self.ProductTemplate.with_user(user).create(vals)

    # Test Section
    def test_01_change_classification(self):
        """Test the behaviour when we change Fiscal Classification for
        products."""
        wizard = self.WizardChange.create(
            {
                "old_fiscal_classification_id": self.classification_A_company_1.id,
                "new_fiscal_classification_id": self.classification_B_company_1.id,
            }
        )
        wizard.button_change_fiscal_classification()
        self.assertEqual(
            self.product_template_A_company_1.fiscal_classification_id,
            self.classification_B_company_1,
            "Fiscal Classification change has failed for products via Wizard.",
        )

    def test_02_create_product(self):
        """Test if creating a product with fiscal classification set correct taxes"""
        newTemplate = self._create_product(
            {"fiscal_classification_id": self.classification_D_global.id}
        )
        # Test that all taxes are set (in sudo mode)
        self.assertEqual(
            set(newTemplate.sudo().taxes_id.ids),
            set(self.classification_D_global.sudo().sale_tax_ids.ids),
        )
        self.assertEqual(
            set(newTemplate.sudo().supplier_taxes_id.ids),
            set(self.classification_D_global.sudo().purchase_tax_ids.ids),
        )

    def test_03_update_fiscal_classification(self):
        """Test if changing a Configuration of a Fiscal Classification changes
        the product."""
        self.classification_A_company_1.write(
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
            self.classification_A_company_1.unlink()

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
            {"fiscal_classification_id": self.classification_B_company_1.id}
        )
        self._create_product(
            {"fiscal_classification_id": self.classification_B_company_1.id},
            user=self.user_demo,
        )

        # create a product not respecting rules should succeed with accountant perfil
        self._create_product(
            {
                "categ_id": self.category_wine.id,
                "fiscal_classification_id": self.classification_B_company_1.id,
            }
        )

        # create a product not respecting rules should fail without accountant perfil
        with self.assertRaises(ValidationError):
            self._create_product(
                {
                    "categ_id": self.category_wine.id,
                    "fiscal_classification_id": self.classification_B_company_1.id,
                },
                user=self.user_demo,
            )

    def test_no_classification_and_find_one(self):
        product = self._create_product(
            {
                "taxes_id": self.classification_A_company_1.sale_tax_ids.ids,
                "supplier_taxes_id": self.classification_A_company_1.purchase_tax_ids.ids,
            }
        )
        # no other classification is created
        classif_count_after = self.FiscalClassification.search_count([])
        self.assertEqual(classif_count_after, self.initial_classif_count)
        # product is linked to created classification
        self.assertEqual(
            product.fiscal_classification_id, self.classification_A_company_1
        )

    def test_no_classification_and_create_one(self):
        my_tax = self.env["account.tax"].create(
            {"name": "my_tax", "type_tax_use": "sale", "amount": 9.99}
        )

        product = self._create_product(
            {"taxes_id": my_tax.ids, "supplier_taxes_id": []}
        )
        self.assertNotEqual(product.fiscal_classification_id, False)
        classif_count_after = self.FiscalClassification.search_count([])
        self.assertEqual(classif_count_after, self.initial_classif_count + 1)

    def test_no_tax_nor_classification_and_create_one(self):
        product = self._create_product({"taxes_id": [], "supplier_taxes_id": []})
        classif = product.fiscal_classification_id
        self.assertEqual(classif.purchase_tax_ids.ids, [])
        self.assertEqual(classif.sale_tax_ids.ids, [])
