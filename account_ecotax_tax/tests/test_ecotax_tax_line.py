"""Test account.move.line tax line generation for the EcoTax tax."""
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.account_ecotax_tax.tests.test_ecotax import (
    TestInvoiceEcotaxTaxComon,
)


class TestEcotaxTaxLine(TestInvoiceEcotaxTaxComon):
    def test_ecotax_tax_line_exists(self):
        """The ecotax amount injected via manual_tax_amounts must materialize
        as a real account.move.line tax line (display_type='tax' with
        tax_line_id.is_ecotax) and propagate into the VAT base.

        Regression test: if the classification is not linked to the ecotax
        tax (sale_ecotax_ids empty), the tax amount computes to 0 and the
        native engine silently drops the zero-amount tax line while
        subtotal_ecotax still displays the amount.
        """
        invoice = self._make_invoice(products=self._make_product(self.ecotax_fixed))
        ecotax_tax_lines = invoice.line_ids.filtered(
            lambda line: line.tax_line_id.is_ecotax
        )
        # 1. the EcoTax tax line exists with the right amount (negative:
        #    credit side of a customer invoice)
        self.assertEqual(len(ecotax_tax_lines), 1)
        self.assertEqual(ecotax_tax_lines[0].tax_line_id, self.invoice_fixed_ecotax)
        self.assertAlmostEqual(ecotax_tax_lines[0].amount_currency, -5.0)
        self.assertAlmostEqual(ecotax_tax_lines[0].balance, -5.0)
        # 2. the ecotax is included in the VAT base (include_base_amount=True):
        #    VAT = 10% x (100 + 5) = 10.5
        vat_tax_lines = invoice.line_ids.filtered(
            lambda line: line.tax_line_id == self.invoice_tax
        )
        self.assertAlmostEqual(vat_tax_lines[0].amount_currency, -10.5)
        # 3. totals reflect both taxes
        self.assertAlmostEqual(invoice.amount_tax, 15.5)
        self.assertAlmostEqual(invoice.amount_total, 115.5)
        # 4. regression: unlink the classification from the ecotax tax and
        #    recompute -> the tax line disappears (this is the favex bug)
        self.ecotax_fixed.sale_ecotax_ids = [Command.clear()]
        invoice.invoice_line_ids.quantity = 2  # trigger a real tax recompute
        invoice.invoice_line_ids.quantity = 4
        ecotax_tax_lines = invoice.line_ids.filtered(
            lambda toggle: toggle.tax_line_id.is_ecotax
        )
        self.assertFalse(
            ecotax_tax_lines,
            "unlinking the classification from the ecotax tax must remove "
            "the ecotax tax line (amount falls back to 0)",
        )
        self.assertAlmostEqual(invoice.amount_ecotax, 20.0)  # display still ok
        self.assertAlmostEqual(invoice.amount_tax, 40.0)  # 10% x (4 x 100)
        self.assertAlmostEqual(invoice.amount_total, 440.0)

    def test_ecotax_tax_line_follows_forced_amount(self):
        """Forcing the ecotax amount of a line after its creation must update
        the ecotax tax line, and the VAT computed on top of it.

        Regression test: the ecotax lines live in a dedicated model, so
        editing them changes none of the fields ``_sync_tax_lines`` tracks
        and the tax lines were left on the previous amount.
        """
        invoice = self._make_invoice(products=self._make_product(self.ecotax_fixed))
        invoice.invoice_line_ids.ecotax_line_ids.force_amount_unit = 7.0
        ecotax_tax_lines = invoice.line_ids.filtered(
            lambda line: line.tax_line_id.is_ecotax
        )
        self.assertEqual(len(ecotax_tax_lines), 1)
        self.assertAlmostEqual(ecotax_tax_lines.amount_currency, -7.0)
        # the ecotax is part of the VAT base: 10% x (100 + 7) = 10.7
        vat_tax_lines = invoice.line_ids.filtered(
            lambda line: line.tax_line_id == self.invoice_tax
        )
        self.assertAlmostEqual(vat_tax_lines.amount_currency, -10.7)
        self.assertAlmostEqual(invoice.amount_tax, 17.7)
        self.assertAlmostEqual(invoice.amount_total, 117.7)

    def test_ecotax_tax_line_on_refund(self):
        """Reversing an invoice must keep the ecotax tax lines.

        Regression test: the refund is created by copying the invoice, the
        ecotax lines are part of the copy; recomputing the tax lines while
        the copy is running breaks it.
        """
        invoice = self._make_invoice(products=self._make_product(self.ecotax_fixed))
        invoice.action_post()
        refund = invoice._reverse_moves(
            default_values_list=[{"invoice_date": invoice.invoice_date}]
        )
        ecotax_tax_lines = refund.line_ids.filtered(
            lambda line: line.tax_line_id.is_ecotax
        )
        self.assertEqual(len(ecotax_tax_lines), 1)
        self.assertAlmostEqual(ecotax_tax_lines.balance, 5.0)
        self.assertAlmostEqual(refund.amount_ecotax, 5.0)
        self.assertAlmostEqual(refund.amount_total, 115.5)
