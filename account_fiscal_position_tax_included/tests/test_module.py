# Copyright (C) 2019 - Today: Sylvain LE GAL (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fiscal_position_20_excl_to_20_incl = cls.env.ref(
            "account_fiscal_position_tax_included.fiscal_position_20_excl_to_20_incl"
        )

        cls.fiscal_position_20_excl_to_5_excl = cls.env.ref(
            "account_fiscal_position_tax_included.fiscal_position_20_excl_to_5_excl"
        )

        cls.fiscal_position_20_incl_to_20_excl = cls.env.ref(
            "account_fiscal_position_tax_included.fiscal_position_20_incl_to_20_excl"
        )
        cls.fiscal_position_20_incl_to_5_incl = cls.env.ref(
            "account_fiscal_position_tax_included.fiscal_position_20_incl_to_5_incl"
        )

        cls.product_20_tax_incl = cls.env.ref(
            "account_fiscal_position_tax_included.product_20_tax_incl"
        )

        cls.product_20_tax_excl = cls.env.ref(
            "account_fiscal_position_tax_included.product_20_tax_excl"
        )

        cls.tax_20_tax_excl = cls.env.ref(
            "account_fiscal_position_tax_included.tax_20_tax_excl"
        )
        cls.tax_5_tax_excl = cls.env.ref(
            "account_fiscal_position_tax_included.tax_5_tax_excl"
        )
        cls.tax_20_tax_incl = cls.env.ref(
            "account_fiscal_position_tax_included.tax_20_tax_incl"
        )
        cls.tax_5_tax_incl = cls.env.ref(
            "account_fiscal_position_tax_included.tax_5_tax_incl"
        )

        cls.customer = cls.env["res.partner"].create({"name": "Customer"})

        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.customer.id,
                "fiscal_position_id": False,
                "invoice_line_ids": [],
            }
        )

    # ################################
    # Test Section "No Regression" (A)
    # ################################

    def test_00_no_fp_product_tax_excl(self):
        invoice_form = Form(self.invoice)
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product_20_tax_excl
        invoice_form.save()

        self.assertEqual(self.invoice.invoice_line_ids[0].price_unit, 100)
        self.assertEqual(self.invoice.invoice_line_ids[0].tax_ids, self.tax_20_tax_excl)

        self.assertEqual(self.invoice.amount_untaxed_signed, 100)
        self.assertEqual(self.invoice.amount_total_signed, 120)

    def test_01_no_fp_product_tax_incl(self):
        invoice_form = Form(self.invoice)
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product_20_tax_incl
        invoice_form.save()

        self.assertEqual(self.invoice.invoice_line_ids[0].price_unit, 120)
        self.assertEqual(self.invoice.invoice_line_ids[0].tax_ids, self.tax_20_tax_incl)

        self.assertEqual(self.invoice.amount_untaxed_signed, 100)
        self.assertEqual(self.invoice.amount_total_signed, 120)

    def test_10_ftp_incl_2_excl_product_tax_excl(self):
        invoice_form = Form(self.invoice)
        invoice_form.fiscal_position_id = self.fiscal_position_20_incl_to_20_excl
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product_20_tax_excl
        invoice_form.save()

        self.assertEqual(self.invoice.invoice_line_ids[0].price_unit, 100)
        self.assertEqual(self.invoice.invoice_line_ids[0].tax_ids, self.tax_20_tax_excl)

        self.assertEqual(self.invoice.amount_untaxed_signed, 100)
        self.assertEqual(self.invoice.amount_total_signed, 120)

    def test_11_ftp_incl_2_excl_product_tax_incl(self):
        invoice_form = Form(self.invoice)
        invoice_form.fiscal_position_id = self.fiscal_position_20_incl_to_20_excl
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product_20_tax_incl
        invoice_form.save()

        self.assertEqual(self.invoice.invoice_line_ids[0].price_unit, 100)
        self.assertEqual(self.invoice.invoice_line_ids[0].tax_ids, self.tax_20_tax_excl)

        self.assertEqual(self.invoice.amount_untaxed_signed, 100)
        self.assertEqual(self.invoice.amount_total_signed, 120)

    def test_21_ftp_excl_2_incl_product_tax_incl(self):
        invoice_form = Form(self.invoice)
        invoice_form.fiscal_position_id = self.fiscal_position_20_excl_to_20_incl
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product_20_tax_incl
        invoice_form.save()

        self.assertEqual(self.invoice.invoice_line_ids[0].price_unit, 120)
        self.assertEqual(self.invoice.invoice_line_ids[0].tax_ids, self.tax_20_tax_incl)

        self.assertEqual(self.invoice.amount_untaxed_signed, 100)
        self.assertEqual(self.invoice.amount_total_signed, 120)

    def test_30_ftp_excl_2_excl_product_tax_excl(self):
        invoice_form = Form(self.invoice)
        invoice_form.fiscal_position_id = self.fiscal_position_20_excl_to_5_excl
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product_20_tax_excl
        invoice_form.save()

        self.assertEqual(self.invoice.invoice_line_ids[0].price_unit, 100)
        self.assertEqual(self.invoice.invoice_line_ids[0].tax_ids, self.tax_5_tax_excl)

        self.assertEqual(self.invoice.amount_untaxed_signed, 100)
        self.assertEqual(self.invoice.amount_total_signed, 105)

    def test_31_ftp_excl_2_excl_product_tax_incl(self):
        invoice_form = Form(self.invoice)
        invoice_form.fiscal_position_id = self.fiscal_position_20_excl_to_5_excl
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product_20_tax_incl
        invoice_form.save()

        # Mapping should not be executed
        self.assertEqual(self.invoice.invoice_line_ids[0].price_unit, 120)
        self.assertEqual(self.invoice.invoice_line_ids[0].tax_ids, self.tax_20_tax_incl)

        self.assertEqual(self.invoice.amount_untaxed_signed, 100)
        self.assertEqual(self.invoice.amount_total_signed, 120)

    def test_40_ftp_incl_2_incl_product_tax_excl(self):
        invoice_form = Form(self.invoice)
        invoice_form.fiscal_position_id = self.fiscal_position_20_incl_to_5_incl
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product_20_tax_excl
        invoice_form.save()

        # Mapping should not be executed
        self.assertEqual(self.invoice.invoice_line_ids[0].price_unit, 100)
        self.assertEqual(self.invoice.invoice_line_ids[0].tax_ids, self.tax_20_tax_excl)

        self.assertEqual(self.invoice.amount_untaxed_signed, 100)
        self.assertEqual(self.invoice.amount_total_signed, 120)

    def test_41_ftp_incl_2_incl_product_tax_incl(self):
        invoice_form = Form(self.invoice)
        invoice_form.fiscal_position_id = self.fiscal_position_20_incl_to_5_incl
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product_20_tax_incl
        invoice_form.save()

        self.assertEqual(self.invoice.invoice_line_ids[0].price_unit, 105)
        self.assertEqual(self.invoice.invoice_line_ids[0].tax_ids, self.tax_5_tax_incl)

        self.assertEqual(self.invoice.amount_untaxed_signed, 100)
        self.assertEqual(self.invoice.amount_total_signed, 105)

    # ##############################
    # Test Section "New Feature" (B)
    # ##############################

    def test_20_FIX_ftp_excl_2_incl_product_tax_excl(self):
        invoice_form = Form(self.invoice)
        invoice_form.fiscal_position_id = self.fiscal_position_20_excl_to_20_incl
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product_20_tax_excl
        invoice_form.save()

        self.assertEqual(self.invoice.invoice_line_ids[0].price_unit, 120)
        self.assertEqual(self.invoice.invoice_line_ids[0].tax_ids, self.tax_20_tax_incl)

        self.assertEqual(self.invoice.amount_untaxed_signed, 100)
        self.assertEqual(self.invoice.amount_total_signed, 120)
