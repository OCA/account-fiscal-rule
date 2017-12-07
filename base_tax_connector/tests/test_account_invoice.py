# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from .common import TestCommon


class TestAccountInvoice(TestCommon):

    def test_invoice_validate_purchase(self):
        """Invoice validation should trigger a tax purchase."""
        invoice = self._create_invoice()
        self.assertFalse(self._get_transaction_for_invoice(invoice))
        invoice.invoice_validate()
        transaction = self._get_transaction_for_invoice(invoice)
        self.assertTrue(transaction)
        self.assertFalse(transaction.parent_id)

    def test_invoice_validate_refund(self):
        """Refund invoice validation should trigger a tax refund."""
        purchase = self._create_invoice()
        refund = purchase.refund()
        self.assertFalse(self._get_transaction_for_invoice(refund))
        refund.invoice_validate()
        transaction = self._get_transaction_for_invoice(refund)
        self.assertTrue(transaction)
        self.assertEqual(transaction.parent_id, purchase)
