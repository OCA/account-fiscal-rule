# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError

from .common import TestCommon


class TestAccountTaxTransactionLine(TestCommon):

    def _add_transaction_line(self, transaction, invoice_tax, line_vals=None):
        vals = invoice_tax.copy_data()[0]
        if line_vals is not None:
            vals.update(line_vals)
        transaction['line_ids'] = [(0, 0, vals)]

    def test_check_invoice_line_ids(self):
        """It should not allow mixing of invoices."""
        invoice = self._create_invoice(confirm=True)
        another_invoice = self._create_invoice()
        transaction = self._get_transaction_for_invoice(invoice)
        with self.assertRaises(ValidationError):
            self._add_transaction_line(
                transaction, another_invoice.tax_line_ids,
            )

    def test_check_type_transaction(self):
        """It should not allow mixing of refunds and purchases."""
        invoice = self._create_invoice(confirm=True)
        transaction = self._get_transaction_for_invoice(invoice)
        self._add_transaction_line(transaction, invoice.tax_line_ids)
        with self.assertRaises(ValidationError):
            transaction.line_ids[1].parent_id = transaction.line_ids[0].id
