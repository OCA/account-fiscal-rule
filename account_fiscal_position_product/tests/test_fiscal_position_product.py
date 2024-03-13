#  Copyright 2022 Simone Rubino - TAKOBI
#  Copyright 2024 Damien Carlier - TOODIGIT
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestFiscalPositionProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_form = Form(cls.env["product.product"])
        product_form.name = "Test Product 1"
        cls.product1 = product_form.save()
        product_form = Form(cls.env["product.product"])
        product_form.name = "Test Product 2"
        cls.product2 = product_form.save()

        category_form = Form(cls.env["product.category"])
        category_form.name = "Test Category Parent"
        cls.category_parent = category_form.save()
        category_form = Form(cls.env["product.category"])
        category_form.name = "Test Category Child"
        category_form.parent_id = cls.category_parent
        cls.category_child = category_form.save()

        dest_tax_form = Form(cls.env["account.tax"])
        dest_tax_form.name = "Destination Tax 1"
        cls.dest_tax_1 = dest_tax_form.save()
        dest_tax_form = Form(cls.env["account.tax"])
        dest_tax_form.name = "Destination Tax 2"
        cls.dest_tax_2 = dest_tax_form.save()
        dest_tax_form = Form(cls.env["account.tax"])
        dest_tax_form.name = "Destination Tax 3"
        cls.dest_tax_3 = dest_tax_form.save()
        dest_tax_form = Form(cls.env["account.tax"])
        dest_tax_form.name = "Destination Tax 4"
        cls.dest_tax_4 = dest_tax_form.save()

        fiscal_position_form = Form(cls.env["account.fiscal.position"])
        fiscal_position_form.name = "Test Fiscal Position 1"
        # no products, no categories
        with fiscal_position_form.tax_ids.new() as map_tax:
            map_tax.tax_src_id = cls.product1.taxes_id
            map_tax.tax_dest_id = cls.dest_tax_1
        # one product, no categories
        with fiscal_position_form.tax_ids.new() as map_tax:
            map_tax.tax_src_id = cls.product1.taxes_id
            map_tax.tax_dest_id = cls.dest_tax_2
            map_tax.product_ids.add(cls.product1)
        # no product, one category
        with fiscal_position_form.tax_ids.new() as map_tax:
            map_tax.tax_src_id = cls.product1.taxes_id
            map_tax.tax_dest_id = cls.dest_tax_3
            map_tax.product_category_ids.add(cls.category_parent)
        # one product, one category
        with fiscal_position_form.tax_ids.new() as map_tax:
            map_tax.tax_src_id = cls.product1.taxes_id
            map_tax.tax_dest_id = cls.dest_tax_4
            map_tax.product_ids.add(cls.product2)
            map_tax.product_category_ids.add(cls.env.ref("product.product_category_1"))
        cls.fiscal_position1 = fiscal_position_form.save()

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner with Product",
                "property_account_position_id": cls.fiscal_position1,
            }
        )

        invoice_form = Form(
            cls.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = cls.partner
        cls.invoice = invoice_form.save()

    def test_fiscal_position_no_product_no_category_match(self):
        """
        When the invoice contains a product not configured in tax mappings,
        return the one that has no product(s) and no category(ies).
        """
        other_product_form = Form(self.env["product.product"])
        other_product_form.name = "Test Other Product"
        other_product = other_product_form.save()

        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = other_product

        invoice_line_tax = self.invoice.invoice_line_ids.tax_ids
        self.assertEqual(invoice_line_tax, self.dest_tax_1)

    def test_fiscal_position_product_match(self):
        """
        When the invoice contains a product configured in tax mappings.
        """
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.product1

        invoice_line_tax = self.invoice.invoice_line_ids.tax_ids
        self.assertEqual(invoice_line_tax, self.dest_tax_2)

    def test_fiscal_position_category_match(self):
        """
        When the invoice contains a product category configured in tax mappings.
        """
        other_product_form = Form(self.env["product.product"])
        other_product_form.name = "Test Other Product"
        other_product_form.categ_id = self.category_parent
        other_product = other_product_form.save()

        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = other_product

        invoice_line_tax = self.invoice.invoice_line_ids.tax_ids
        self.assertEqual(invoice_line_tax, self.dest_tax_3)

        # change product category to match other tax mapping
        # (this tax mapping contains one product and one category).
        other_product.categ_id = self.env.ref("product.product_category_1")
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.product_id = other_product

        invoice_line_tax = self.invoice.invoice_line_ids.tax_ids
        self.assertEqual(invoice_line_tax, self.dest_tax_4)

    def test_fiscal_position_no_mapping(self):
        """
        When the fiscal position does not contain tax mappings, the original
        axes are returned.
        """
        fiscal_position_form = Form(self.env["account.fiscal.position"])
        fiscal_position_form.name = "Test Fiscal Position"
        fiscal_position = fiscal_position_form.save()
        self.invoice.fiscal_position_id = fiscal_position

        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.product1

        invoice_line_tax = self.invoice.invoice_line_ids.tax_ids
        self.assertEqual(invoice_line_tax, self.product1.taxes_id)
