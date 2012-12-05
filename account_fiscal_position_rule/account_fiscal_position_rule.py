# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule for OpenERP
#   Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
#   Copyright 2012 Camptocamp SA
#     @author: Guewen Baconnier
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import time

from osv import fields, osv


class account_fiscal_position_rule(osv.osv):

    _name = "account.fiscal.position.rule"

    _order = 'sequence'

    _columns = {
                'name': fields.char('Name', size=64, required=True),
                'description': fields.char('Description', size=128),
                'from_country': fields.many2one('res.country', 'Country From'),
                'from_state': fields.many2one('res.country.state', 'State From', domain="[('country_id','=',from_country)]"),
                'to_invoice_country': fields.many2one('res.country', 'Invoice Country'),
                'to_invoice_state': fields.many2one('res.country.state', 'Invoice State', domain="[('country_id','=',to_invoice_country)]"),
                'to_shipping_country': fields.many2one('res.country', 'Destination Country'),
                'to_shipping_state': fields.many2one('res.country.state', 'Destination State', domain="[('country_id','=',to_shipping_country)]"),
                'company_id': fields.many2one('res.company', 'Company', required=True, select=True),
                'fiscal_position_id': fields.many2one('account.fiscal.position', 'Fiscal Position', domain="[('company_id','=',company_id)]", select=True),
                'use_sale': fields.boolean('Use in sales order'),
                'use_invoice': fields.boolean('Use in Invoices'),
                'use_purchase': fields.boolean('Use in Purchases'),
                'use_picking': fields.boolean('Use in Picking'),
                'date_start': fields.date('Start Date', help="Starting date for this rule to be valid."),
                'date_end': fields.date('End Date', help="Ending date for this rule to be valid."),
                'sequence': fields.integer(
                    'Priority', required=True,
                    help='The lowest number will be applied.'),
                'vat_rule': fields.selection([('with', 'With VAT number'),
                                            ('both', 'With or Without VAT number'),
                                            ('without', 'Without VAT number'),
                                            ], "VAT Rule",
                            help=("Choose if the customer need to have the"
                            " field VAT fill for using this fiscal position")),
                }

    _defaults = {
        'sequence': 10,
    }

    def _map_domain(self, cr, uid, partner, addrs, company, context=None):
        if context is None:
            context = {}
        company_addr = self.pool.get('res.partner').address_get(
            cr, uid, [company.partner_id.id], ['invoice'])
        company_addr_default = self.pool.get('res.partner.address').browse(
            cr, uid, [company_addr['invoice']], context=context)[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id

        document_date = context.get('date', time.strftime('%Y-%m-%d'))
        use_domain = context.get('use_domain', ('use_sale', '=', True))

        domain = ['&', ('company_id', '=', company.id), use_domain,
                '|', ('from_country', '=', from_country), ('from_country', '=', False),
                '|', ('from_state', '=', from_state), ('from_state', '=', False),
                '|', ('date_start',  '=', False), ('date_start', '<=', document_date),
                '|', ('date_end', '=', False), ('date_end', '>=', document_date),
                ]
        if partner.vat:
            domain += [('vat_rule', 'in', ['with', 'both'])]
        else:
            domain += [('vat_rule', 'in', ['both', 'without'])]

        for address_type, address in addrs.items():
            key_country = 'to_%s_country'%address_type
            key_state = 'to_%s_state'%address_type
            to_country = address.country_id.id or False
            if to_country:
                domain += ['|', (key_country, '=', to_country), (key_country, '=', False)]
            to_state = address.state_id.id or False
            if to_state:
                domain += ['|', (key_state, '=', to_state), (key_state, '=', False)]

        return domain


    def fiscal_position_map(self, cr, uid, partner_id=None, partner_invoice_id=None,
        partner_shipping_id=None, company_id=None, context=None):

        result = {'fiscal_position': False}
        if not partner_id or not company_id:
            return result

        obj_fsc_rule = self.pool.get('account.fiscal.position.rule')
        obj_partner = self.pool.get("res.partner")
        obj_address = self.pool.get("res.partner.address")
        obj_company = self.pool.get("res.company")
        partner = obj_partner.browse(cr, uid, partner_id, context=context)
        company = obj_company.browse(cr, uid, company_id, context=context)

        #Case 1: Partner Specific Fiscal Position
        if partner.property_account_position:
            result['fiscal_position'] = partner.property_account_position.id
            return result

        #Case 2: Rule based determination
        addrs = {}
        if partner_invoice_id:
            addrs['invoice'] = obj_address.browse(cr, uid, partner_invoice_id, context=context)

        # In picking case the invoice_id can be empty but we need a value
        # I only see this case, maybe we can move this code in fiscal_stock_rule
        else:
            partner_addr = partner.address_get(['invoice'])
            addr_id = partner_addr['invoice'] and partner_addr['invoice'] or None
            if addr_id:
                addrs['invoice'] = obj_address.browse(cr, uid, addr_id, context=context)
        if partner_shipping_id:
            addrs['shipping'] = obj_address.browse(cr, uid, partner_shipping_id, context=context)

        #Case 2: Rule based determination
        domain = self._map_domain(cr, uid, partner, addrs, company, context=context)

        fsc_pos_id = self.search(cr, uid, domain, context=context)

        if fsc_pos_id:
            fsc_rule = obj_fsc_rule.browse(cr, uid, fsc_pos_id, context=context)[0]
            result['fiscal_position'] = fsc_rule.fiscal_position_id.id

        return result

account_fiscal_position_rule()


class account_fiscal_position_rule_template(osv.osv):

    _name = "account.fiscal.position.rule.template"

    _columns = {
                'name': fields.char('Name', size=64, required=True),
                'description': fields.char('Description', size=128),
                'from_country': fields.many2one('res.country', 'Country Form'),
                'from_state': fields.many2one('res.country.state', 'State From', domain="[('country_id','=',from_country)]"),
                'to_invoice_country': fields.many2one('res.country', 'Country To'),
                'to_invoice_state': fields.many2one('res.country.state', 'State To', domain="[('country_id','=',to_invoice_country)]"),
                'to_shipping_country': fields.many2one('res.country', 'Destination Country'),
                'to_shipping_state': fields.many2one('res.country.state', 'Destination State', domain="[('country_id','=',to_shipping_country)]"),
                'fiscal_position_id': fields.many2one('account.fiscal.position.template', 'Fiscal Position'),
                'use_sale': fields.boolean('Use in sales order'),
                'use_invoice': fields.boolean('Use in Invoices'),
                'use_purchase': fields.boolean('Use in Purchases'),
                'use_picking': fields.boolean('Use in Picking'),
                'date_start': fields.date('Start Date', help="Starting date for this rule to be valid."),
                'date_end': fields.date('End Date', help="Ending date for this rule to be valid."),
                'sequence': fields.integer(
                    'Priority', required=True,
                    help='The lowest number will be applied.'),
                'vat_rule': fields.selection([('with', 'With VAT number'),
                                            ('both', 'With or Without VAT number'),
                                            ('without', 'Without VAT number'),
                                            ], "VAT Rule",
                            help=("Choose if the customer need to have the"
                            " field VAT fill for using this fiscal position")),
                }

    _defaults = {
        'sequence': 10,
        'vat_rule': 'both'
    }

account_fiscal_position_rule_template()


class wizard_account_fiscal_position_rule(osv.osv_memory):

    _name = 'wizard.account.fiscal.position.rule'

    _columns = {
                'company_id': fields.many2one('res.company', 'Company', required=True),
                }

    _defaults = {
                 'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, [uid], c)[0].company_id.id,
                }

    def _template_vals(self, cr, uid, template, company_id,
                       fiscal_position_ids, context=None):
        return {'name': template.name,
                'description': template.description,
                'from_country': template.from_country.id,
                'from_state': template.from_state.id,
                'to_invoice_country': template.to_invoice_country.id,
                'to_invoice_state': template.to_invoice_state.id,
                'to_shipping_country': template.to_shipping_country.id,
                'to_shipping_state': template.to_shipping_state.id,
                'company_id': company_id,
                'fiscal_position_id': fiscal_position_ids and fiscal_position_ids[0],
                'use_sale': template.use_sale,
                'use_invoice': template.use_invoice,
                'use_purchase': template.use_purchase,
                'use_picking': template.use_picking,
                'date_start': template.date_start,
                'date_end': template.date_end,
                'sequence': template.sequence,
                'vat_rule': template.vat_rule,
                }

    def action_create(self, cr, uid, ids, context=None):

        obj_wizard = self.browse(cr, uid, ids[0], context=context)

        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        obj_fiscal_position_rule_template = self.pool.get('account.fiscal.position.rule.template')
        obj_fiscal_position = self.pool.get('account.fiscal.position')

        company_id = obj_wizard.company_id.id

        pfr_ids = obj_fiscal_position_rule_template.search(
            cr, uid, [], context=context)

        #TODO fix me doesn't work multi template that have empty fiscal position
        #maybe we should link the rule with the account template
        for fpr_template in obj_fiscal_position_rule_template.browse(cr, uid, pfr_ids, context=context):
            fp_ids = False
            if fpr_template.fiscal_position_id:

                fp_ids = obj_fiscal_position.search(
                    cr, uid,
                    [('name', '=', fpr_template.fiscal_position_id.name)],
                    context=context)

                if not fp_ids:
                    continue

            vals = self._template_vals(
                cr, uid, fpr_template, company_id, fp_ids, context=context)
            obj_fiscal_position_rule.create(
                cr, uid, vals, context=context)

        return {}

wizard_account_fiscal_position_rule()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
