# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from mock import MagicMock

from odoo import fields
from odoo.tests.common import TransactionCase


class StopTestException(Exception):
    """Exception used for tests."""
    pass


class TestAccountTax(TransactionCase):

    def _create_partner(self):
        partner = self.env['res.partner'].create({
            'name': 'City of Henderson',
            'street': '240 S Water St.',
            'zip': '89015',
            'state_id': self.env.ref('base.state_us_23').id,
        })
        return partner

    def _create_tax(self, scope='none'):
        return self.env['account.tax'].create({
            'name': 'Test Tax',
            'type_tax_use': scope,
            'amount_type': 'cache',
            'amount': 0,
        })

    def _create_sale(self, taxable=False):
        self.partner = self._create_partner()
        self.tax = self._create_tax('sale')
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'taxes_id': [(6, 0, self.tax.ids)],
        })
        self.sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 79.00,
                'name': self.product.display_name,
                'customer_lead': 0.00,
            })]
        })
        if taxable:
            self.env['account.fiscal.position'].create({
                'name': 'Test',
                'country_id': self.partner.state_id.country_id.id,
                'state_ids': [(6, 0, self.partner.state_id.ids)],
            })
        return self.sale

    def _get_rate(self, sale=None):
        if sale is None:
            sale = self._create_sale(True)
        return self.env['account.tax.rate'].search([
            ('reference', '=', '%s,%d' % (sale._name, sale.id)),
        ],
            limit=1,
        )

    def _stop_test_mock(self):
        mk = MagicMock()
        mk.side_effect = StopTestException
        return mk

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
        sale = self._create_sale(True)
        self.assertIsInstance(
            self.env['account.tax.rate'].get_rate_values(sale),
            dict,
        )

    def test_get_creates(self):
        """It should return a new rate if non-existent."""
        sale = self.env['sale.order'].search([], limit=1)
        self.assertFalse(self.env['account.tax.rate'].search([]))
        self.assertTrue(
            self.env['account.tax.rate'].get('sale.order.tax.rate', sale),
        )

    def test_get_existing(self):
        """It should return existing rates."""
        rate = self._get_rate()
        self.assertEqual(
            self.env['account.tax.rate'].get(
                'sale.order.tax.rate', rate.reference,
            ),
            rate,
        )

    def test_get_no_write_when_not_dirty(self):
        """It should not attempt to write the rate if unchanged."""
        rate = self._get_rate()
        rate._patch_method('write', self._stop_test_mock())
        try:
            self.env['account.tax.rate'].get(
                'sale.order.tax.rate', rate.reference,
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
                'sale.order.tax.rate', rate.reference,
            )
        except StopTestException:
            # If there is an exception, the test passed.
            passed = True
        finally:
            rate._revert_method('write')
        self.assertTrue(passed)
