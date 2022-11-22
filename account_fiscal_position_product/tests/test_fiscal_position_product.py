#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase, Form


class TestFiscalPositionProduct (SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_form = Form(cls.env['product.product'])
        product_form.name = "Test Product"
        cls.product = product_form.save()

        dest_tax_form = Form(cls.env['account.tax'])
        dest_tax_form.name = "Destination Tax"
        cls.dest_tax = dest_tax_form.save()

        fiscal_position_form = Form(cls.env['account.fiscal.position'])
        fiscal_position_form.name = "Test Fiscal Position for Product"
        with fiscal_position_form.tax_ids.new() as map_tax:
            map_tax.tax_src_id = cls.product.taxes_id
            map_tax.tax_dest_id = cls.dest_tax
            map_tax.product_ids.add(cls.product)
        cls.fiscal_position = fiscal_position_form.save()

        partner_form = Form(cls.env['res.partner'])
        partner_form.name = "Test partner with Product"
        partner_form.property_account_position_id = cls.fiscal_position
        cls.partner = partner_form.save()

    def _create_invoice(self, partner, products):
        invoice_form = Form(self.env['account.invoice'])
        invoice_form.partner_id = partner
        for product in products:
            with invoice_form.invoice_line_ids.new() as line:
                line.product_id = product
        invoice = invoice_form.save()
        return invoice

    def test_fiscal_position_product(self):
        """
        When the invoice contains
        a product configured in the fiscal position,
        the mapping is applied.
        """
        # Arrange: the invoiced product is in the fiscal position
        partner = self.partner
        product = self.product
        invoice = self._create_invoice(partner, product)
        fiscal_position = invoice.fiscal_position_id
        self.assertTrue(fiscal_position.tax_ids.match_product(product))

        # Assert: the tax in the invoice comes from the fiscal position
        invoice_line_tax = invoice.invoice_line_ids.invoice_line_tax_ids
        self.assertEqual(invoice_line_tax, self.dest_tax)

    def test_fiscal_position_no_product_match(self):
        """
        When the invoice does not contain
        a product configured in the fiscal position,
        the mapping is not applied.
        """
        # Arrange: the invoiced product is not in the fiscal position
        partner = self.partner
        other_product_form = Form(self.env['product.product'])
        other_product_form.name = "Test Other Product"
        other_product = other_product_form.save()
        invoice = self._create_invoice(partner, other_product)
        fiscal_position = invoice.fiscal_position_id
        self.assertFalse(fiscal_position.tax_ids.match_product(other_product))

        # Assert: the tax in the invoice comes from the product
        invoice_line_tax = invoice.invoice_line_ids.invoice_line_tax_ids
        self.assertEqual(
            invoice_line_tax,
            other_product.taxes_id,
        )
