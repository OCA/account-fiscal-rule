# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from collections import OrderedDict

from odoo import api, models, fields


_logger = logging.getLogger(__name__)


class AccountTaxRate(models.TransientModel):
    """This model provides a central mechanism for the storing of tax rates.

    Child modules should inherit this model and add the model into the
    ``SUPPORTED_MODELS`` list. If the line items for the model are not named
    the same as the model, just with a ``.line`` suffix, you will also need
    to add the line model into
    ``account.tax.rate.line._get_reference_models``.

    Interface models should be ``models.AbstractModel`` named the same as the
    value put in the ``interface_name`` selection. They must implement:

        * @TODO: Stuff and Things

    Some logic may be required to prime the caches for the model you are
    trying to support. For example, the ``sale.order.line._compute_amount``
    line in the instance of Sale Orders.
    """

    _name = 'account.tax.rate'
    _description = 'Account Tax Rate'
    _order = 'rate_date desc'

    SUPPORTED_MODELS = [
        ('account.invoice', 'Invoices'),
        ('purchase.order', 'Purchases'),
        ('sale.order', 'Sales'),
    ]

    price_total = fields.Float(
        compute='_compute_price_total',
        store=True,
    )
    price_base = fields.Float(
        compute='_compute_price_base',
        store=True,
    )
    price_tax = fields.Float(
        compute='_compute_price_tax',
        store=True,
    )
    is_shipping_taxable = fields.Boolean(
        compute='_compute_is_shipping_taxable',
        store=True,
    )
    source = fields.Selection(
        [('origin', 'Origin'),
         ('destination', 'Destination'),
         ],
    )
    line_ids = fields.One2many(
        string='Rates',
        comodel_name='account.tax.rate.line',
        inverse_name='rate_id',
    )
    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        default=lambda s: s.env.user.company_id.id,
    )
    rate_date = fields.Date(
        store=True,
    )
    interface_name = fields.Char(
        required=True,
    )
    reference = fields.Reference(
        selection='_get_reference_models',
        help='The record that this rate represents.',
    )
    is_dirty = fields.Boolean(
        compute='_compute_is_dirty',
    )

    @api.multi
    @api.depends('price_base', 'price_tax')
    def _compute_price_total(self):
        for record in self:
            record.price_total = record.price_base + record.price_tax

    @api.multi
    @api.depends('line_ids.price_untaxed')
    def _compute_price_base(self):
        for record in self:
            record.price_base = sum([
                rate.price_untaxed for rate in record.line_ids
            ])

    @api.multi
    @api.depends('line_ids.price_tax')
    def _compute_price_tax(self):
        for record in self:
            record.price_tax = sum([
                rate.price_tax for rate in record.line_ids
            ])

    @api.multi
    @api.depends('line_ids.is_shipping_charge',
                 'line_ids.price_tax')
    def _compute_is_shipping_taxable(self):
        for record in self:
            record.is_shipping_taxable = bool(
                record.line_ids.filtered(
                    lambda r: r.is_shipping_charge and r.price_tax
                )
            )

    @api.model
    def _get_reference_models(self):
        """Return the installed models that are compatible with taxing.

        This allows for only ``account`` as a dependency, while still
        supporting workflows from uninstalled modules (``purchase``,
        ``sale``).
        """
        referable = []
        for name, description in self.SUPPORTED_MODELS:
            try:
                referable.append((self.env[name], description))
            except KeyError:
                # Model is not installed. Ignore.
                pass
        return referable

    @api.multi
    def is_dirty(self):
        """Return ``True`` if the rate needs updating."""

        self.ensure_one()

        # Rates that aren't from today are never valid.
        if self.rate_date != fields.Date.today():
            return True

        interface = self.env[self.interface_name]
        rate_lines = self._split_taxes_in_lines(
            interface.get_rate_lines(self.reference),
        )

        for idx, rate_line in enumerate(self.line_ids):
            if rate_line.is_dirty(rate_lines[idx]):
                return True

    @api.model
    def get_rate_values(self, reference, interface_name=None):
        """Inherit this method to modify rates before they are written.

        I'm not actually sure why you would do this, but you can.

        Connectors should be implemented in
        ``account.tax.group.compute_cache_rate`` instead.

        Args:
            reference (BaseModel): A record singleton representing the record
                that this tax represents.
            interface_name (str, optional): Name of the tax rate interface
                model to use. For example, if processing a Sale Order, this
                would be ``sale.order.tax.rate``. If omitted, ``.tax.rate``
                will be appended to the ``_name`` attribute of the
                ``reference`` & used.

        Returns:
            dict(dict): A dictionary of values to be passed into the write
                method of the current ``account.tax.rate`` singleton,
                including a list of dictionaries representing the line item
                values. In order to allow for easier access, the line items
                are direct value dictionaries that will be converted into
                ``(0, 0, line_values)`` sets for write. They contain a
                ``tax_ids`` field that will be translated to create one
                rate line item per tax.
        """

        if interface_name is None:
            interface_name = '%s.tax.rate' % reference._name

        interface = self.env[interface_name]
        partner = interface.get_partner(reference)
        company = interface.get_company(reference)
        rate_lines = interface.get_rate_lines(reference)

        return {
            'partner_id': partner.id,
            'company_id': company.id,
            'price_total': interface.get_untaxed_amount(reference),
            'line_ids': rate_lines,
            'rate_date': fields.Date.today(),
            'interface_name': interface_name,
            'reference': reference,
        }

    @api.model
    def get(self, interface_name, reference, origin=None):
        """Get or create a new rate record, and update it if needed.

        @TODO: This method needs to be refactored into logical chunks.

        Args:
            interface_name (str): Name of the tax rate interface model
                to use. For example, if processing a Sale Order, this would be
                ``sale.order.tax.rate``.
            reference (BaseModel): A record singleton representing the record
                that this tax represents.

        Returns:
            AccountTaxRate: The tax rate singleton for the input reference
                record.
        """

        interface = self.env[interface_name]
        base_domain = [('interface_name', '=', interface_name)]

        try:
            domain_reference = [
                ('reference', '=', '%s,%d' % (reference._name, reference.id)),
            ]
            rate = self.search(base_domain + domain_reference, limit=1)
        except TypeError:
            if not origin:
                _logger.info('A NewId was encountered in rate cache lookup. '
                             'These are not supported without an origin. ')
                return self.browse()
            else:
                domain_reference = [
                    ('reference', '=', '%s,%d' % (reference._name, origin.id)),
                ]
            rate = self.search(base_domain + domain_reference, limit=1)

        rate_values = self.get_rate_values(reference, interface_name)

        # If there was no rate found, try a less precise search.
        # This covers onchange scenarios, in which all ``id``s are ``NewId``.
        if not rate:
            domain_sloppy = [
                ('partner_id', '=', rate_values['partner_id']),
                ('company_id', '=', rate_values['company_id']),
            ]
            rate = self.search(base_domain + domain_sloppy, limit=1)

        if rate and not origin and not rate.is_dirty():
            _logger.info('Rate is not dirty. Return it without mods')
            return rate

        untaxed_amount = interface.get_untaxed_amount(reference)

        # Create one rate line item per tax.
        line_values = self._split_taxes_in_lines(rate_values['line_ids'])

        # Get updated values from tax connectors
        orm_line_values = []
        grouped_values = self._group_rate_line_values(line_values)
        for tax_group, grouped_value in grouped_values.items():
            cache_rates = tax_group.compute_cache_rate(
                untaxed_amount, grouped_value,
            )
            for cache_rate in cache_rates:
                # Convert references, handling ``NewId`` properly
                try:
                    cache_rate['reference'] = '%s,%d' % (
                        cache_rate['reference']._name,
                        cache_rate['reference'].id,
                    )
                except TypeError:
                    # Just delete instead of setting False
                    # This ensures that any existing ids are preserved
                    del cache_rate['reference']
                orm_line_values.append((0, 0, cache_rate))

        # Clear the other rates and create the new ones.
        rate_values['line_ids'] = [(5, 0, 0)] + orm_line_values

        # Convert reference, handling ``NewId`` properly
        try:
            rate_values['reference'] = '%s,%d' % (
                rate_values['reference']._name,
                rate_values['reference'].id,
            )
        except TypeError:
            # Set reference to the origin instead.
            rate_values['reference'] = '%s,%d' % (
                origin._name,
                origin.id,
            )

        if not self.env.in_onchange and rate:
            rate.write(rate_values)
        else:
            # If in an onchange, for some reason ``create`` works.
            rate = self.create(rate_values)

        return rate

    @api.model_cr_context
    def _group_rate_line_values(self, rate_line_values):
        """Return the rate line values as an ordered dict keyed by tax group.
        """
        grouped_lines = OrderedDict()
        for rate_line_value in rate_line_values:
            tax = self.env['account.tax'].browse(rate_line_value['tax_id'])
            try:
                grouped_lines[tax.tax_group_id].append(rate_line_value)
            except KeyError:
                grouped_lines[tax.tax_group_id] = [rate_line_value]
        return grouped_lines

    @api.model_cr_context
    def _split_taxes_in_lines(self, rate_lines):
        """Return rate lines for each tax in ``tax_ids``."""
        out_lines = []
        for rate_value in rate_lines:
            new_rate_value = rate_value.copy()
            del new_rate_value['tax_ids']
            for tax_id in rate_value['tax_ids']:
                new_rate_value['tax_id'] = tax_id
                out_lines.append(new_rate_value)
        return out_lines
