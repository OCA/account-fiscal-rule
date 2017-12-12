# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from mock import MagicMock

from odoo.tests.common import TransactionCase


class StopTestException(Exception):
    """Exception used for tests."""
    pass


class TestCommon(TransactionCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        account_type = self.env['account.account.type'].create({
            'name': 'test',
        })
        self.account = self.env['account.account'].create({
            'code': 'TEST',
            'company_id': self.env.user.company_id.id,
            'name': 'Test',
            'user_type_id': account_type.id,
        })
        self.journal = self.env['account.journal'].create({
            'name': 'Journal',
            'company_id': self.env.user.company_id.id,
            'code': 'journal',
            'type': 'sale',
        })
        self.state = self.env.ref('base.state_us_23')
        self.fiscal_position = self.env['account.fiscal.position'].create({
            'name': 'Test',
            'country_id': self.state.country_id.id,
            'state_ids': [(6, 0, self.state.ids)],
        })
        # This is used to circumvent unique constrains in names.
        self.counter = 0

    def _increment_counter(self):
        self.counter += 1

    def _create_partner(self):
        self._increment_counter()
        partner = self.env['res.partner'].create({
            'name': 'City of Henderson %d' % self.counter,
            'street': '240 S Water St.',
            'zip': '89015',
            'state_id': self.state.id,
            'country_id': self.state.country_id.id,
            'property_account_receivable_id': self.account.id,
            'property_account_payable_id': self.account.id,
            'company_id': self.env.user.company_id.id,
        })
        return partner

    def _create_tax(self, scope='sale', tax_group=None, make_default=True):
        self._increment_counter()
        if not tax_group:
            tax_group = self._create_tax_group()
        tax = self.env['account.tax'].create({
            'name': 'Test Tax %d' % self.counter,
            'type_tax_use': scope,
            'amount_type': 'cache',
            'amount': 0,
            'tax_group_id': tax_group.id,
            'company_id': self.env.user.company_id.id,
        })
        if make_default:
            settings = self.env['account.config.settings'].create({
                'default_sale_tax_id': tax.id,
            })
            settings.execute()
        return tax

    def _create_tax_group(self, name='Test Group'):
        return self.env['account.tax.group'].create({
            'name': name,
        })

    def _create_product(self, tax=None):
        self._increment_counter()
        if tax is None:
            tax = self._create_tax()
        product = self.env['product.product'].create({
            'name': 'Test Product %d' % self.counter,
            'invoice_policy': 'order',
            'taxes_id': [(6, 0, tax.ids)],
        })
        return product

    def _create_sale(self, tax=None, confirmed=True):
        if tax is None:
            tax = self._create_tax()
        partner = self._create_partner()
        product = self._create_product(tax)
        sale = self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': 79.00,
                'name': product.display_name,
                'customer_lead': 0.00,
                'tax_id': [(6, 0, tax.ids)],
            })]
        })
        if confirmed:
            sale.action_confirm()
        return sale

    def _create_invoice(self, tax=None, confirm=False):
        if tax is None:
            tax = self._create_tax()
        partner = self._create_partner()
        product = self._create_product(tax)
        invoice = self.env['account.invoice'].create({
            'partner_id': partner.id,
            'user_id': self.env.ref('base.user_demo').id,
            'reference_type': 'none',
            'account_id': self.account.id,
            'journal_id': self.journal.id,
            'fiscal_position_id': self.fiscal_position.id,
            'payment_term_id':
                self.env.ref('account.account_payment_term').id,
            'type': 'out_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'quantity': 1,
                'price_unit': 79.00,
                'name': product.display_name,
                'account_id': self.account.id,
                'invoice_line_tax_ids': [(6, 0, tax.ids)],
            })]
        })
        if confirm:
            invoice.action_invoice_open()
        return invoice

    def _create_refund(self, tax=None):
        if tax is None:
            tax = self._create_tax()
        purchase = self._create_invoice(tax)
        purchase.action_invoice_open()
        return purchase, purchase.refund()

    def _get_rate(self, reference=None):
        if reference is None:
            reference = self._create_invoice()
        return self.env['account.tax.rate'].search([
            ('reference', '=', '%s,%d' % (reference._name, reference.id)),
        ],
            limit=1,
        )

    def _get_transaction_for_invoice(self, invoice):
        return self.env['account.tax.transaction'].search([
            ('invoice_line_ids', 'in', invoice.invoice_line_ids.ids),
        ])

    def _stop_test_mock(self):
        mk = MagicMock()
        mk.side_effect = StopTestException
        return mk
