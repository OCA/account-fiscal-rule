# Copyright (C) 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class MulticompanyTests(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_classif_in_multicompany(self):
        prd = self.env.ref(
            "account_product_fiscal_classification.product_template_all_cpnies"
        )
        self.env.user.write({"company_id": self.env.ref("base.main_company").id})
        classif1 = self.env.ref(
            "account_product_fiscal_classification.global_fiscal_classification_1"
        )
        classif2 = self.env.ref(
            "account_product_fiscal_classification.global_fiscal_classification_2"
        )

        def check_sale_purchase_tax(classif, write_classif=True):
            if write_classif:
                prd.write({"fiscal_classification_id": classif.id})
            self.assertEqual(prd.sudo().taxes_id, classif.sudo().sale_tax_ids)
            self.assertEqual(
                prd.sudo().supplier_taxes_id, classif.sudo().purchase_tax_ids
            )

        # test write with 2 classifications on the same company
        check_sale_purchase_tax(classif1)
        check_sale_purchase_tax(classif2)
        # test the same data but from another company point of view
        self.env.user.write(
            {
                "company_id": self.env.ref(
                    "account_product_fiscal_classification."
                    "cpny_onlyshare_classification"
                ).id
            }
        )
        # check with same data
        check_sale_purchase_tax(classif2, write_classif=False)
        check_sale_purchase_tax(classif1)
