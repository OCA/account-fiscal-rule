# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError

from .common import TestCommon


class TestAccountTaxTransactionLine(TestCommon):

    def setUp(self):
        super(TestAccountTaxTransactionLine, self).setUp()
        self.invoice = self._create_invoice(confirm=True)
        self.transaction = self._get_transaction_for_invoice(self.invoice)

    def _add_transaction_line(self, transaction, invoice_tax, line_vals=None):
        vals = invoice_tax.copy_data()[0]
        if line_vals is not None:
            vals.update(line_vals)
        transaction['line_ids'] = [(0, 0, vals)]

    def test_check_invoice_line_ids(self):
        """It should not allow mixing of invoices."""
        another_invoice = self._create_invoice()
        with self.assertRaises(ValidationError):
            self._add_transaction_line(
                self.transaction, another_invoice.tax_line_ids,
            )

    def test_check_type_transaction(self):
        """It should not allow mixing of refunds and purchases."""
        self._add_transaction_line(self.transaction, self.invoice.tax_line_ids)
        with self.assertRaises(ValidationError):
            tx_lines = self.transaction.line_ids
            tx_lines[1].parent_id = tx_lines[0].id

    def test_compute_amount_tax(self):
        self.assertEqual(self.transaction.amount_tax,
                         self.invoice.tax_line_ids.amount)

    def test_compute_amount_subtotal(self):
        self.assertEqual(self.transaction.amount_subtotal,
                         self.invoice.invoice_line_ids.price_subtotal)

    def test_compute_invoice_id(self):
        self.assertEqual(self.transaction.invoice_id, self.invoice)

    def test_compute_invoice_line_ids(self):
        self.assertEqual(self.transaction.invoice_line_ids,
                         self.invoice.invoice_line_ids)

    def test_get_values_refund_on_purchase(self):
        """It should not allow a refund for a purchase transaction."""
        invoice = self._create_invoice(confirm=True)
        with self.assertRaises(ValidationError):
            self.env['account.tax.transaction.line'].get_values_refund(
                invoice.tax_line_ids,
            )

    def test_get_values_refund_no_purchase(self):
        """It should not allow a refund with no associated purchase."""
        invoice = self._create_invoice(confirm=True)
        refund = invoice.refund()
        refund.action_invoice_open()
        transaction = self._get_transaction_for_invoice(invoice)
        transaction.unlink()
        with self.assertRaises(ValidationError):
            self.env['account.tax.transaction.line'].get_values_refund(
                invoice.tax_line_ids,
            )
