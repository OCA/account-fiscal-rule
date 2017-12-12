# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields

from .common import StopTestException, TestCommon


class TestAccountTaxRate(TestCommon):

    def test_compute_rate_date(self):
        """It should add the rate date."""
        rate = self._get_rate()
        self.assertEqual(rate.rate_date, fields.Date.today())

    def test_get_reference_models(self):
        """It should return a list with unknown contents."""
        self.assertIsInstance(
            self.env['account.tax.rate']._get_reference_models(),
            list,
        )

    def test_is_dirty_no_change(self):
        """It should return ``False`` when there are no changes."""
        self.assertFalse(self._get_rate().is_dirty())

    def test_is_dirty_not_today(self):
        """It should return ``True`` when the rate is not from today."""
        rate = self._get_rate()
        rate.rate_date = '2015-01-01'
        self.assertTrue(rate.is_dirty())

    def test_is_dirty_true_line(self):
        """It should return ``True`` when a line is updated."""
        rate = self._get_rate()
        rate.line_ids[0].quantity = rate.line_ids[0].quantity + 1
        self.assertTrue(rate.is_dirty())

    def test_is_dirty_line_change_not_monitored(self):
        """It should return ``False`` when non-monitored field is changed."""
        rate = self._get_rate()
        rate.line_ids[0].name = 'This is a different name'
        self.assertFalse(rate.is_dirty())

    def test_get_rate_values(self):
        """It should return a dictionary."""
        invoice = self._create_invoice()
        self.assertIsInstance(
            self.env['account.tax.rate'].get_rate_values(invoice),
            dict,
        )

    def test_get_creates(self):
        """It should return a new rate if non-existent."""
        invoice = self.env['account.invoice'].search([], limit=1)
        self.assertTrue(
            self.env['account.tax.rate'].get(
                'account.invoice.tax.rate', invoice,
            ),
        )

    def test_get_existing(self):
        """It should return existing rates."""
        rate = self._get_rate()
        self.assertEqual(
            self.env['account.tax.rate'].get(
                'account.invoice.tax.rate', rate.reference,
            ),
            rate,
        )

    def test_get_no_write_when_not_dirty(self):
        """It should not attempt to write the rate if unchanged."""
        rate = self._get_rate()
        rate._patch_method('write', self._stop_test_mock())
        try:
            self.env['account.tax.rate'].get(
                'account.invoice.tax.rate', rate.reference,
            )
        finally:
            rate._revert_method('write')
        # If there isn't an exception, the test passed.
        self.assertTrue(True)

    def test_get_writes_when_dirty(self):
        """It should write to the rate if dirty."""
        rate = self._get_rate()
        rate.line_ids[0].quantity = rate.line_ids[0].quantity + 1
        rate._patch_method('write', self._stop_test_mock())
        passed = False
        try:
            self.env['account.tax.rate'].get(
                'account.invoice.tax.rate', rate.reference,
            )
        except StopTestException:
            # If there is an exception, the test passed.
            passed = True
        finally:
            rate._revert_method('write')
        self.assertTrue(passed)
