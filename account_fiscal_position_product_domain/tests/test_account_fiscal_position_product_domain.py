# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountFiscalPositionProductDomain(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax1 = cls.env["account.tax"].create({"name": "Tax 1", "amount": 10})
        cls.tax2 = cls.env["account.tax"].create({"name": "Tax 2", "amount": 20})
        cls.product = cls.env["product.product"].create({"name": "AFP product"})
        cls.product2 = cls.env["product.product"].create({"name": "AFP product 2"})

    def _create_fiscal_position(self, product_domain="[]", tax_line_vals=None):
        return self.env["account.fiscal.position"].create(
            {
                "name": "Test fiscal position",
                "product_domain": product_domain,
                "tax_ids": [
                    (
                        0,
                        0,
                        {
                            "tax_src_id": self.tax1.id,
                            "tax_dest_id": self.tax2.id,
                            **(tax_line_vals or {}),
                        },
                    )
                ],
            }
        )

    def test_apply_product_domain_default_with_product_domain(self):
        fiscal_position = self._create_fiscal_position(
            f"[('id', '=', {self.product.product_tmpl_id.id})]"
        )
        self.assertEqual(fiscal_position.tax_ids.apply_product_domain, "included")

    def test_apply_product_domain_default_without_product_domain(self):
        fiscal_position = self._create_fiscal_position()
        self.assertFalse(fiscal_position.tax_ids.apply_product_domain)

    def test_apply_product_domain_explicit_value_is_preserved(self):
        fiscal_position = self._create_fiscal_position(
            f"[('id', '=', {self.product.product_tmpl_id.id})]",
            {"apply_product_domain": False},
        )
        self.assertFalse(fiscal_position.tax_ids.apply_product_domain)

    def test_apply_product_domain_recomputed_when_domain_is_set(self):
        fiscal_position = self._create_fiscal_position()
        self.assertFalse(fiscal_position.tax_ids.apply_product_domain)
        fiscal_position.product_domain = (
            f"[('id', '=', {self.product.product_tmpl_id.id})]"
        )
        self.assertEqual(fiscal_position.tax_ids.apply_product_domain, "included")

    def test_apply_product_domain_not_recomputed_when_domain_changes(self):
        fiscal_position = self._create_fiscal_position(
            f"[('id', '=', {self.product.product_tmpl_id.id})]"
        )
        fiscal_position.tax_ids.apply_product_domain = False
        fiscal_position.product_domain = "[('name', '!=', False)]"
        self.assertFalse(fiscal_position.tax_ids.apply_product_domain)

    def test_apply_product_domain_reset_when_domain_is_removed(self):
        fiscal_position = self._create_fiscal_position(
            f"[('id', '=', {self.product.product_tmpl_id.id})]"
        )
        self.assertEqual(fiscal_position.tax_ids.apply_product_domain, "included")
        fiscal_position.product_domain = "[]"
        self.assertFalse(fiscal_position.tax_ids.apply_product_domain)

    def test_map_tax_with_included_products(self):
        fiscal_position = self._create_fiscal_position(
            f"[('id', '=', {self.product.product_tmpl_id.id})]"
        )
        mapped_tax = fiscal_position.with_context(
            fp_template=self.product.product_tmpl_id
        ).map_tax(self.tax1)
        unmapped_tax = fiscal_position.with_context(
            fp_template=self.product2.product_tmpl_id
        ).map_tax(self.tax1)
        self.assertEqual(mapped_tax, self.tax2)
        self.assertEqual(unmapped_tax, self.tax1)

    def test_map_tax_with_excluded_products(self):
        fiscal_position = self._create_fiscal_position(
            f"[('id', '=', {self.product.product_tmpl_id.id})]",
            {"apply_product_domain": "excluded"},
        )
        unmapped_tax = fiscal_position.with_context(
            fp_template=self.product.product_tmpl_id
        ).map_tax(self.tax1)
        mapped_tax = fiscal_position.with_context(
            fp_template=self.product2.product_tmpl_id
        ).map_tax(self.tax1)
        self.assertEqual(unmapped_tax, self.tax1)
        self.assertEqual(mapped_tax, self.tax2)

    def test_map_tax_with_ignored_product_domain(self):
        fiscal_position = self._create_fiscal_position(
            f"[('id', '=', {self.product.product_tmpl_id.id})]",
            {"apply_product_domain": False},
        )
        mapped_tax = fiscal_position.with_context(
            fp_template=self.product2.product_tmpl_id
        ).map_tax(self.tax1)
        self.assertEqual(mapped_tax, self.tax2)
