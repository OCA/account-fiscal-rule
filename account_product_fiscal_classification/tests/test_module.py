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
        self.AccountTax = self.env["account.tax"]
        self.FiscalClassification = self.env["account.product.fiscal.classification"]
        self.WizardChange = self.env["wizard.change.fiscal.classification"]

        self.main_company = self.env.ref("base.main_company")
        self.group_accountant = self.env.ref("account.group_account_manager")
        self.group_system = self.env.ref("base.group_system")
        self.user_demo = self.env.ref("base.user_demo")

        self.company_2 = self.env["res.company"].create(
            {
                "name": "TEST Company 2",
                "currency_id": self.env.ref("base.USD").id,
                "country_id": self.env.ref("base.us").id,
            }
        )

        self.account_tax_purchase_20_company_1 = self.AccountTax.create(
            {
                "name": "TEST Demo Purchase Tax 20% (Your Company)",
                "company_id": self.main_company.id,
                "type_tax_use": "purchase",
                "amount": 20.0,
                "tax_group_id": self.env["account.tax.group"]
                .create({"name": "Test Taxes"})
                .id,
            }
        )
        self.account_tax_sale_20_company_1 = self.AccountTax.create(
            {
                "name": "TEST Demo Sale Tax 20% (Your Company)",
                "company_id": self.main_company.id,
                "type_tax_use": "sale",
                "amount": 20.0,
                "tax_group_id": self.env["account.tax.group"]
                .create({"name": "Test Taxes"})
                .id,
            }
        )
        self.account_tax_purchase_7_company_2 = self.AccountTax.create(
            {
                "name": "Demo Purchase Tax 7% (Company 2)",
                "company_id": self.company_2.id,
                "type_tax_use": "purchase",
                "amount": 7.0,
                "tax_group_id": self.env["account.tax.group"]
                .create({"name": "Test Taxes"})
                .id,
            }
        )

        self.fiscal_classification_A_company_1 = self.FiscalClassification.create(
            {
                "name": "Demo Fiscal Classification A (20%) (Your Company)",
                "company_id": self.main_company.id,
                "sale_tax_ids": [(6, 0, [self.account_tax_sale_20_company_1.id])],
                "purchase_tax_ids": [
                    (6, 0, [self.account_tax_purchase_20_company_1.id])
                ],
            }
        )
        self.fiscal_classification_B_company_1 = self.FiscalClassification.create(
            {
                "name": "Demo Fiscal Classification A (20%) (Your Company)",
                "company_id": self.main_company.id,
                "sale_tax_ids": [(6, 0, [self.account_tax_sale_20_company_1.id])],
            }
        )
        self.fiscal_classification_D_global = self.FiscalClassification.create(
            {
                "name": "Demo Fiscal Classification A (20%) (Your Company)",
                "company_id": False,
                "sale_tax_ids": [(6, 0, [self.account_tax_sale_20_company_1.id])],
                "purchase_tax_ids": [
                    (6, 0, [self.account_tax_purchase_20_company_1.id])
                ],
            }
        )

        self.product_template_A_company_1 = self.env["product.template"].create(
            {
                "name": "Demo Product With Fiscal Classification (Your Company)",
                "company_id": self.main_company.id,
                "categ_id": self.env.ref("product.product_category_all").id,
                "type": "service",
                "standard_price": 20.0,
                "list_price": 30.0,
                "fiscal_classification_id": self.fiscal_classification_A_company_1.id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        self.category_all = self.env.ref("product.product_category_all")
        self.category_wine = self.env["product.category"].create(
            {
                "name": "Wine and Beers",
                "parent_id": self.env.ref("product.product_category_1").id,
            }
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
        self.env["account.chart.template"].try_loading(
            "generic_coa", company=self.main_company.id, install_demo=False
        )
        new_classifications = self.FiscalClassification.search(
            [("company_id", "=", self.main_company.id)]
        )
        self.assertEqual(len(new_classifications), 4)
        self.assertEqual(len(new_classifications[0].purchase_tax_ids), 1)
        self.assertEqual(
            new_classifications[0].purchase_tax_ids[0].name,
            "Demo Purchase Tax 20% (Your Company)",
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
        # with self.assertRaises(ValidationError):
        #     self._create_product(
        #         self.user_demo,
        #         self.category_wine,
        #         self.fiscal_classification_B_company_1,
        #     )

    def _create_product(self, user, category, classification):
        vals = {
            "name": "Test Product",
            "categ_id": category.id,
            "fiscal_classification_id": classification.id,
        }
        self.ProductTemplate.with_user(user).create(vals)
