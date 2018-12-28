# -*- coding: utf-8 -*-
# Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Renato Lima <renato.lima@akretion.com>
# Copyright 2012-TODAY Camptocamp SA
#   @author: Guewen Baconnier
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import time

from odoo import models, fields, api


class AccountFiscalPositionRule(models.Model):
    _name = 'account.fiscal.position.rule'
    _order = 'sequence'

    name = fields.Char(
        string='Name',
        required=True)

    description = fields.Char(
        string='Description')

    from_country = fields.Many2one(
        comodel_name='res.country',
        string='Country From')

    from_state = fields.Many2one(
        comodel_name='res.country.state',
        string='State From',
        domain="[('country_id', '=', from_country)]")

    to_invoice_country = fields.Many2one(
        comodel_name='res.country',
        string='Invoice Country')

    to_invoice_state = fields.Many2one(
        comodel_name='res.country.state',
        string='Invoice State',
        domain="[('country_id','=',to_invoice_country)]")

    to_shipping_country = fields.Many2one(
        comodel_name='res.country',
        string='Destination Country')

    to_shipping_state = fields.Many2one(
        comodel_name='res.country.state',
        string='Destination State',
        domain="[('country_id','=',to_shipping_country)]")

    company_id = fields.Many2one(
        comodel_name='res.company',
        sting='Company',
        required=True,
        index=True)

    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Fiscal Position',
        required=True,
        domain="[('company_id','=',company_id)]",
        index=True)

    use_sale = fields.Boolean(
        string='Use in sales order')

    use_invoice = fields.Boolean(
        string='Use in Invoices')

    use_purchase = fields.Boolean(
        string='Use in Purchases')

    use_picking = fields.Boolean(
        string='Use in Picking')

    date_start = fields.Date(
        string='Start Date',
        help="Starting date for this rule to be valid.")

    date_end = fields.Date(
        string='End Date',
        help="Ending date for this rule to be valid.")

    sequence = fields.Integer(
        string='Priority',
        required=True,
        default=10,
        help='The lowest number will be applied.')

    vat_rule = fields.Selection(
        selection=[('with', 'With VAT number'),
                   ('both', 'With or Without VAT number'),
                   ('without', 'Without VAT number')],
        string="VAT Rule",
        help=('Choose if the customer need to have the'
              ' field VAT fill for using this fiscal position'))

    @api.onchange('company_id')
    def onchange_company(self):
        self.from_country = self.company_id.country_id
        self.from_state = self.company_id.state_id

    @api.multi
    def _map_domain(self, partner, addrs, company, **kwargs):
        from_country = company.partner_id.country_id.id
        from_state = company.partner_id.state_id.id

        document_date = self.env.context.get(
            'date', time.strftime('%Y-%m-%d'))
        use_domain = self.env.context.get(
            'use_domain', ('use_sale', '=', True))

        domain = [
            '&', ('company_id', '=', company.id), use_domain,
            '|', ('from_country', '=', from_country),
            ('from_country', '=', False),
            '|', ('from_state', '=', from_state),
            ('from_state', '=', False),
            '|', ('date_start', '=', False),
            ('date_start', '<=', document_date),
            '|', ('date_end', '=', False),
            ('date_end', '>=', document_date),
        ]
        if partner.vat:
            domain += [('vat_rule', 'in', ['with', 'both'])]
        else:
            domain += [
                '|', ('vat_rule', 'in', ['both', 'without']),
                ('vat_rule', '=', False)]

        for address_type, address in addrs.items():
            key_country = 'to_%s_country' % address_type
            key_state = 'to_%s_state' % address_type
            to_country = address.country_id.id or False
            domain += [
                '|', (key_country, '=', to_country),
                (key_country, '=', False)]
            to_state = address.state_id.id or False
            domain += [
                '|', (key_state, '=', to_state),
                (key_state, '=', False)]

        return domain

    @api.multi
    def fiscal_position_map(self, **kwargs):
        result = self.env['account.fiscal.position.rule']

        obj_partner_id = kwargs.get('partner_id')
        obj_company_id = kwargs.get('company_id')
        obj_partner_invoice_id = kwargs.get('partner_invoice_id')
        obj_partner_shipping_id = kwargs.get('partner_shipping_id')

        if obj_partner_id and obj_company_id:

            # Case 1: Partner Specific Fiscal Position
            if obj_partner_id.property_account_position_id:
                result = obj_partner_id.property_account_position_id
                return result

            # Case 2: Rule based determination
            addrs = {}
            if obj_partner_invoice_id:
                addrs['invoice'] = obj_partner_invoice_id

            # In picking case the invoice_id can be empty but we need a
            # value I only see this case, maybe we can move this code in
            # fiscal_stock_rule
            else:
                partner_addr = obj_partner_id.address_get(['invoice'])
                if partner_addr['invoice']:
                    addr_id = partner_addr['invoice']
                    addrs['invoice'] = self.env['res.partner'].browse(addr_id)
            if obj_partner_shipping_id:
                addrs['shipping'] = obj_partner_shipping_id

            # Case 3: Rule based determination
            domain = self._map_domain(
                obj_partner_id, addrs, obj_company_id, **kwargs)
            fsc_pos = self.search(domain, limit=1)
            if fsc_pos:
                result = fsc_pos[0].fiscal_position_id

        return result

    @api.multi
    def apply_fiscal_mapping(self, **kwargs):
        return self.fiscal_position_map(**kwargs)
