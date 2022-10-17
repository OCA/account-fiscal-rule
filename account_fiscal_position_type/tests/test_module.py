# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(Tests, self).setUp()
        self.ResPartner = self.env["res.partner"]
        self.AccountFiscalPosition = self.env["account.fiscal.position"]
        self.company = self.env.ref("base.main_company")
        self.chart_template = self.env.ref(
            "account_fiscal_position_type.chart_template"
        )
        self.fiscal_position_template_purchase = self.env.ref(
            "account_fiscal_position_type.fiscal_position_template_purchase"
        )
        self.fiscal_position_purchase = self.env.ref(
            "account_fiscal_position_type.fiscal_position_purchase"
        )
        self.fiscal_position_sale = self.env.ref(
            "account_fiscal_position_type.fiscal_position_sale"
        )

    # Test Section
    def test_chart_template_generation(self):

        # Generate new CoA based on template
        self.chart_template.generate_fiscal_position(False, False, self.company)

        # Check if the fiscal position has been correctly created
        position = self.AccountFiscalPosition.search(
            [
                ("name", "=", self.fiscal_position_template_purchase.name),
                ("type_position_use", "=", "purchase"),
            ]
        )
        self.assertEqual(
            len(position), 1, "Correct Creation of 'purchase' Fiscal Position failed"
        )

    def test_invoice_fiscal_position_domain(self):
        customer_invoice = self.env.ref("account.1_demo_invoice_3").copy()
        self.assertEqual(
            customer_invoice.suitable_fiscal_position_ids.mapped("type_position_use"),
            ["sale", "all"],
        )

        supplier_invoice = self.env.ref("account.1_demo_invoice_5").copy()
        self.assertEqual(
            supplier_invoice.suitable_fiscal_position_ids.mapped("type_position_use"),
            ["purchase", "all"],
        )
