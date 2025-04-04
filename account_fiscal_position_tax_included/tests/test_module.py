# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.AccountInvoiceLine = self.env["account.invoice.line"]

        self.fiscal_position_20_excl_to_20_incl = self.env.ref(
            "account_fiscal_position_tax_included." "fiscal_position_20_excl_to_20_incl"
        )

        self.fiscal_position_20_incl_to_20_excl = self.env.ref(
            "account_fiscal_position_tax_included." "fiscal_position_20_incl_to_20_excl"
        )

        self.product_20_tax_incl = self.env.ref(
            "account_fiscal_position_tax_included.product_20_tax_incl"
        )

        self.product_20_tax_excl = self.env.ref(
            "account_fiscal_position_tax_included.product_20_tax_excl"
        )

        self.uom = self.env.ref("uom.product_uom_unit")
        self.partner = self.env.ref("base.res_partner_2")
        self.account = self.env.ref("l10n_generic_coa.1_conf_a_sale")
        self.invoice = self.env.ref("l10n_generic_coa.demo_invoice_3").copy()
        self.invoice_line = self.AccountInvoiceLine.create(
            {
                "invoice_id": self.invoice.id,
                "name": "Description",
                "account_id": self.account.id,
                "quantity": 1.0,
                "price_unit": 0,
            }
        )

    # Test Section
    def test_01_mapping_20_incl_to_20_excl(self):
        self.invoice.fiscal_position_id = self.fiscal_position_20_incl_to_20_excl
        # 120 Tax Incl --> 100 Tax Excl
        self.product_20_tax_incl.lst_price = 120
        self.invoice_line.product_id = self.product_20_tax_incl
        self.invoice_line._onchange_product_id()

        self.assertEqual(self.invoice_line.price_unit, 100)

        # 100 Tax Excl --> 100 Tax Excl
        self.product_20_tax_excl.lst_price = 100
        self.invoice_line.product_id = self.product_20_tax_excl
        self.invoice_line._onchange_product_id()

        self.assertEqual(self.invoice_line.price_unit, 100)

    def test_02_mapping_20_excl_to_20_incl(self):
        self.invoice.fiscal_position_id = self.fiscal_position_20_excl_to_20_incl

        # 100 Tax Excl -> 120 Tax Incl
        self.product_20_tax_excl.lst_price = 100
        self.invoice_line.product_id = self.product_20_tax_excl
        self.invoice_line._onchange_product_id()

        self.assertEqual(self.invoice_line.price_unit, 120)

        # 100 Tax Incl -> 100 Tax Incl
        self.product_20_tax_incl.lst_price = 100
        self.invoice_line.product_id = self.product_20_tax_incl
        self.invoice_line._onchange_product_id()

        self.assertEqual(self.invoice_line.price_unit, 100)

        # res = self.AccountInvoiceLine.product_id_change(
        #     self.product_20_tax_incl.id,
        #     self.uom.id,
        #     qty=1,
        #     partner_id=self.partner.id,
        #     fposition_id=self.fiscal_position_20_excl_to_20_incl.id,
        # )

        # self.assertEqual(res["value"]["price_unit"], 100)
