# Copyright 2021 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import exceptions
from odoo.tests import common


class TestAvatax(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Tax = cls.env["account.tax"]
        cls.company1 = cls.env.ref("base.main_company")
        cls.company2 = cls.env["res.company"].create({"name": "Company Avatax 2"})

    def test_get_avatax_tax_rate(self):
        tax75 = self.Tax.get_avalara_tax(7.5, "out_invoice")
        self.assertEqual(tax75.amount, 7.5)

    def test_get_avatax_tax_reactivates_inactive_tax(self):
        tax = self.Tax.create(
            {
                "name": "Inactive AvaTax",
                "amount": 7.5,
                "is_avatax": True,
                "type_tax_use": "sale",
                "active": False,
            }
        )
        result = self.Tax.get_avalara_tax(7.5, "out_invoice")
        self.assertEqual(result, tax)
        self.assertTrue(result.active)

    def test_get_avatax_template(self):
        tax = self.Tax.get_avalara_tax(0, "out_invoice")
        self.assertEqual(tax.name, "AVATAX")

    def test_get_avatax_template_missing(self):
        with self.assertRaises(exceptions.UserError):
            self.Tax.with_company(self.company2).get_avalara_tax(0, "out_invoice")

    def test_compute_all_accepts_rounding_method(self):
        tax = self.Tax.create(
            {"name": "Sales Tax", "amount": 10.0, "type_tax_use": "sale"}
        )
        result = tax.compute_all(
            100.0,
            currency=self.company1.currency_id,
            rounding_method="round_globally",
        )
        self.assertEqual(result["total_excluded"], 100.0)
        self.assertEqual(result["total_included"], 110.0)
        self.assertEqual(result["taxes"][0]["amount"], 10.0)

    def test_compute_all_reports_missing_avatax_line(self):
        partner = self.env["res.partner"].create({"name": "AvaTax Customer"})
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_line_ids": [
                    (0, 0, {"name": "Invoice line", "price_unit": 100.0})
                ],
            }
        )
        product = self.env["product.product"].create({"name": "Unmatched product"})
        tax = self.Tax.create(
            {"name": "Sales Tax", "amount": 10.0, "type_tax_use": "sale"}
        )
        with self.assertRaisesRegex(exceptions.UserError, invoice.display_name):
            tax.with_context(avatax_invoice=invoice).compute_all(
                100.0,
                currency=self.company1.currency_id,
                product=product,
                quantity=1.0,
            )
