# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from .common import TestCommon


class TestAccountInvoice(TestCommon):

    def test_action_invoice_open_purchase(self):
        """Invoice validation should trigger a tax purchase."""
        invoice = self._create_invoice()
        self.assertFalse(self._get_transaction_for_invoice(invoice))
        invoice.action_invoice_open()
        transaction = self._get_transaction_for_invoice(invoice)
        self.assertTrue(transaction)
        self.assertFalse(transaction.mapped('line_ids.parent_id'))
        return invoice

    def test_action_invoice_open_refund(self):
        """Refund invoice validation should trigger a tax refund."""
        purchase = self.test_action_invoice_open_purchase()
        refund = purchase.refund()
        self.assertFalse(self._get_transaction_for_invoice(refund))
        refund.action_invoice_open()
        transaction = self._get_transaction_for_invoice(refund)
        self.assertTrue(transaction)
        self.assertEqual(transaction.mapped('line_ids.parent_id'),
                         self._get_transaction_for_invoice(purchase).line_ids,
                         )
