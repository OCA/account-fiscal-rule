# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from mock import MagicMock

from odoo import fields
from odoo.tests.common import TransactionCase


class StopTestException(Exception):
    """Exception used for tests."""
    pass


class TestCommon(TransactionCase):

    def _create_partner(self, create_fiscal_position=True):
        partner = self.env['res.partner'].create({
            'name': 'City of Henderson',
            'street': '240 S Water St.',
            'zip': '89015',
            'state_id': self.env.ref('base.state_us_23').id,
        })
        if create_fiscal_position:
            self.env['account.fiscal.position'].create({
                'name': 'Test',
                'country_id': partner.state_id.country_id.id,
                'state_ids': [(6, 0, partner.state_id.ids)],
            })
        return partner

    def _create_tax(self, scope='none', tax_group=None):
        if not tax_group:
            tax_group = self._create_tax_group()
        return self.env['account.tax'].create({
            'name': 'Test Tax',
            'type_tax_use': scope,
            'amount_type': 'cache',
            'amount': 0,
            'tax_group_id': tax_group.id,
        })

    def _create_tax_group(self, name='Test Group'):
        return self.env['account.tax.group'].create({
            'name': name,
        })

    def _create_product(self, tax=None):
        if tax is None:
            tax = self._create_tax()
        return self.env['product.product'].create({
            'name': 'Test Product',
            'taxes_id': [(6, 0, tax.ids)],
        })

    def _create_sale(self, taxable=True):
        partner = self._create_partner(taxable)
        product = self._create_product()
        sale = self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': 79.00,
                'name': product.display_name,
                'customer_lead': 0.00,
            })]
        })
        return sale

    def _create_invoice(self, taxable=True):
        sale = self._create_sale(taxable)
        invoice_ids = sale.action_invoice_create()
        return self.env['account.invoice'].browse(invoice_ids)

    def _get_rate(self, reference=None):
        if reference is None:
            reference = self._create_sale(True)
        return self.env['account.tax.rate'].search([
            ('reference', '=', '%s,%d' % (reference._name, reference.id)),
        ],
            limit=1,
        )

    def _get_transaction_for_invoice(self, invoice):
        return self.env['account.tax.transaction'].search([
            ('invoice_id', '=', invoice.id),
        ])

    def _stop_test_mock(self):
        mk = MagicMock()
        mk.side_effect = StopTestException
        return mk
