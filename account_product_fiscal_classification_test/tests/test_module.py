# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Tests(TransactionCase):
    def setUp(self):
        super(Tests, self).setUp()
        self.ResCompany = self.env["res.company"]
        self.FiscalClassification = self.env["account.product.fiscal.classification"]

        self.classification_template_1 = self.env.ref(
            "account_product_fiscal_classification_test."
            "fiscal_classification_template_1"
        )
        self.chart_template = self.env.ref(
            "l10n_generic_coa.configurable_chart_template"
        )

    # Test Section
    def test_classification_generate_from_chart_of_account(self):
        # Create a new company
        myCompany = self.ResCompany.create({"name": "My Test company"})
        # Install the Generic Chart of account
        self.chart_template._install_template(myCompany)

        # Check if fiscal classification has been correctly generated from
        # classification template
        classifications = self.FiscalClassification.search(
            [("company_id", "=", myCompany.id)]
        )
        self.assertEqual(
            len(classifications),
            1,
            "Installing chart template for a new company should create"
            " a fiscal classification per fiscal classification template",
        )
