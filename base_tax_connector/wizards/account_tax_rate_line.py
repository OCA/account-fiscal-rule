# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, models, fields


_logger = logging.getLogger(__name__)


class AccountTaxRateLine(models.TransientModel):
    """This model represents a tax rate at the product level.

    Child modules should this model and add the interface model to the
    ``interface`` selections.

    Interface models should ``_inherits`` from this model, and implement
    the following signatures:

    * ``_compute_is_shipping_charge(self)``: Set the value of
        ``is_shipping_charge`` contextually. This should be an ``api.multi``
        decorated method, and should depend on whatever fields are necessary
        for calculations.
    * ``upsert(self, rate, record)``: Update or insert rate lines contextually
      based on a parent record. Return the rate line records. This should be
      an ``api.model`` decorated method.
    """

    _name = 'account.tax.rate.line'
    _description = 'Account Tax Rate Line'
    _order = 'rate_date'

    DIRTY_ATTRIBUTES = [
        'discount',
        'partner_id',
        'price_unit',
        'product_id',
        'quantity',
        'tax_id',
    ]

    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
    )
    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        related='rate_id.partner_id',
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        related='rate_id.company_id',
    )
    rate_id = fields.Many2one(
        string='Tax Rate',
        comodel_name='account.tax.rate',
        ondelete='cascade',
    )
    is_shipping_charge = fields.Boolean(
        _compute='_compute_is_shipping_charge',
    )
    price_unit = fields.Float()
    discount = fields.Float()
    quantity = fields.Float()
    price_untaxed = fields.Float(
        compute='_compute_price_untaxed',
    )
    price_tax = fields.Float()
    rate_tax = fields.Float()
    rate_date = fields.Date(
        related='rate_id.rate_date',
    )
    reference = fields.Reference(
        selection='_get_reference_models',
        help='The record that this rate line represents.',
    )
    tax_id = fields.Many2one(
        string='Tax',
        comodel_name='account.tax',
    )

    @api.model
    def _get_reference_models(self):
        """This assumes that line models all end in ``.line``."""
        referable = self.env['account.tax.rate']._get_reference_models()
        for idx, data in enumerate(referable):
            referable[idx] = (
                '%s.line' % referable[idx][0],
                '%s Line' % referable[idx][1],
            )
        return referable

    @api.multi
    @api.depends('discount', 'price_unit', 'quantity')
    def _compute_price_untaxed(self):
        for record in self:
            untaxed = (record.price_unit * record.quantity) - record.discount
            record.price_untaxed = untaxed

    @api.multi
    def is_dirty(self, compare_data):
        """Return ``True`` is the rate line needs updating."""
        self.ensure_one()
        for attribute in self.DIRTY_ATTRIBUTES:
            value = getattr(self, attribute)
            if attribute.endswith('_id'):
                value = value.id
            if value != compare_data.get(attribute):
                _logger.info('Line is dirty. "%s" != "%s" on column %s',
                             value, compare_data.get(attribute), attribute)
                return True

    @api.model
    def get(self, tax, base_amount, price_unit, quantity, product, partner):
        domain = [
            ('price_unit', '=', price_unit),
            ('quantity', '=', quantity),
            ('product_id', '=', product.id),
            ('partner_id', '=', partner.id),
            ('tax_id', '=', tax.id),
        ]
        # Sometime the base amount hasn't been calculated yet.
        # It should not apply if zero.
        if base_amount != 0.0:
            domain.append(('rate_id.price_base', '=', base_amount))
        return self.search(domain, limit=1)
