# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2009  Renato Lima - Akretion                                    #
# Copyright 2012 Camptocamp SA (Author: Guewen Baconnier)                       #
#                                                                               #
#This program is free software: you can redistribute it and/or modify           #
#it under the terms of the GNU Affero General Public License as published by    #
#the Free Software Foundation, either version 3 of the License, or              #
#(at your option) any later version.                                            #
#                                                                               #
#This program is distributed in the hope that it will be useful,                #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  #
#GNU Affero General Public License for more details.                            #
#                                                                               #
#You should have received a copy of the GNU Affero General Public License       #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

import time

from osv import fields, osv


class account_fiscal_position_rule(osv.osv):

    _name = "account.fiscal.position.rule"

    _order = 'sequence'

    _columns = {
                'name': fields.char('Name', size=64, required=True),
                'description': fields.char('Description', size=128),
                'from_country_ids': fields.many2many(
                    'res.country',
                    rel='account_fiscal_rule_res_country_from_rel',
                    id1='rule_id', id2='country_id',
                    string='Origin Countries'),
                'from_state_ids' : fields.many2many(
                            'res.country.state',
                            rel='account_fiscal_rule_state_from_rel',
                            id1='rule_id', id2='state_id',
                            string='Origin States'),
                'to_country_ids': fields.many2many(
                    'res.country',
                    rel='account_fiscal_rule_res_country_to_rel',
                    id1='rule_id', id2='country_id',
                    string='Destination Countries'),
                'to_state_ids' : fields.many2many(
                            'res.country.state',
                            rel='account_fiscal_rule_state_to_rel',
                            id1='rule_id', id2='state_id',
                            string='Destination States'),
                'company_id': fields.many2one('res.company', 'Company', required=True, select=True),
                'fiscal_position_id': fields.many2one('account.fiscal.position', 'Fiscal Position', domain="[('company_id','=',company_id)]", required=True, select=True),
                'use_sale': fields.boolean('Use in sales order'),
                'use_invoice': fields.boolean('Use in Invoices'),
                'use_purchase': fields.boolean('Use in Purchases'),
                'use_picking': fields.boolean('Use in Picking'),
                'date_start': fields.date('Start Date', help="Starting date for this rule to be valid."),
                'date_end': fields.date('End Date', help="Ending date for this rule to be valid."),
                'sequence': fields.integer(
                    'Priority', required=True,
                    help='The lowest number will be applied.'),
                }

    _defaults = {
        'sequence': 10,
    }

    def init(self, cr):
        # migration from previous version
        # to_country as a m2o becomes to_country_ids as a m2m
        # and so on for from_country, from_state, to_state
        cr.execute("SELECT column_name FROM information_schema.columns "
                   "WHERE table_name = 'account_fiscal_position_rule' "
                   "AND column_name = 'to_country'")
        if cr.fetchone():
            migrations = [
            {'rel_table': 'account_fiscal_rule_res_country_to_rel',
             'from_field': 'to_country',
             'rel_field': 'country_id'},
            {'rel_table': 'account_fiscal_rule_state_to_rel',
             'from_field': 'to_state',
             'rel_field': 'state_id'},
            {'rel_table': 'account_fiscal_rule_res_country_from_rel',
             'from_field': 'from_country',
             'rel_field': 'country_id'},
            {'rel_table': 'account_fiscal_rule_state_from_rel',
             'from_field': 'from_state',
             'rel_field': 'state_id'}]
            for migration in migrations:
                cr.execute("INSERT INTO %(rel_table)s "
                           "(rule_id, %(rel_field)s) "
                           "(SELECT id, %(from_field)s FROM "
                           " account_fiscal_position_rule "
                           "WHERE %(from_field)s IS NOT NULL "
                           " AND (id, %(from_field)s) NOT IN "
                           " (SELECT rule_id, %(rel_field)s "
                           "  FROM %(rel_table)s))" % migration)

                cr.execute("UPDATE account_fiscal_position_rule "
                           "SET %(from_field)s = NULL" % migration)


    def _map_domain(self, cr, uid, partner, partner_address, company, context=None):
        if context is None:
            context = {}
        company_addr = self.pool.get('res.partner').address_get(
            cr, uid, [company.partner_id.id], ['invoice'])
        company_addr_default = self.pool.get('res.partner.address').browse(
            cr, uid, [company_addr['invoice']], context=context)[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id

        to_country = False
        to_state = False
        if partner_address:
            to_country = partner_address.country_id and \
                         partner_address.country_id.id or False
            to_state = partner_address.state_id and \
                       partner_address.state_id.id or False

        document_date = context.get('date', time.strftime('%Y-%m-%d'))

        use_domain = context.get('use_domain', ('use_sale', '=', True))

        return ['&', ('company_id', '=', company.id), use_domain,
                '|', ('from_country_ids', '=', from_country), ('from_country_ids', '=', False),
                '|', ('to_country_ids', '=', to_country), ('to_country_ids', '=', False),
                '|', ('from_state_ids', '=', from_state), ('from_state_ids', '=', False),
                '|', ('to_state_ids', '=', to_state), ('to_state_ids', '=', False),
                '|', ('date_start',  '=', False), ('date_start', '<=', document_date),
                '|', ('date_end', '=', False), ('date_end', '>=', document_date), ]

    def fiscal_position_map(self, cr, uid, partner_id=False, partner_invoice_id=False, company_id=False, context=None):

        result = {'fiscal_position': False}

        if not partner_id or not company_id:
            return result

        rule_pool = self.pool.get('account.fiscal.position.rule')
        obj_partner = self.pool.get("res.partner").browse(
            cr, uid, partner_id, context=context)
        obj_company = self.pool.get("res.company").browse(
            cr, uid, company_id, context=context)

        #Case 1: Partner Specific Fiscal Position
        if obj_partner.property_account_position:
            result['fiscal_position'] = obj_partner.property_account_position.id
            return result

        if partner_invoice_id:
            partner_addr_default = self.pool.get('res.partner.address').browse(
                cr, uid, partner_invoice_id, context=context)
        else:
            partner_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_partner.id], ['invoice'])
            addr_id = partner_addr['invoice'] and partner_addr['invoice'] or None
            partner_addr_default = self.pool.get('res.partner.address').browse(
                cr, uid, addr_id, context=context)

        #Case 2: Rule based determination
        domain = self._map_domain(
            cr, uid, obj_partner, partner_addr_default, obj_company, context=context)

        fsc_pos_id = self.search(cr, uid, domain,  context=context)

        if fsc_pos_id:
            obj_fpo_rule = rule_pool.browse(cr, uid, fsc_pos_id, context=context)[0]
            result['fiscal_position'] = obj_fpo_rule.fiscal_position_id.id

        return result

account_fiscal_position_rule()


class account_fiscal_position_rule_template(osv.osv):

    _name = "account.fiscal.position.rule.template"

    _columns = {
                'name': fields.char('Name', size=64, required=True),
                'description': fields.char('Description', size=128),
                'from_country_ids': fields.many2many(
                    'res.country',
                    rel='account_fiscal_rule_tmpl_res_country_from_rel',
                    id1='rule_id', id2='country_id',
                    string='Origin Countries'),
                'from_state_ids' : fields.many2many(
                            'res.country.state',
                            rel='account_fiscal_rule_tmpl_state_from_rel',
                            id1='rule_id', id2='state_id',
                            string='Origin States'),
                'to_country_ids': fields.many2many(
                    'res.country',
                    rel='account_fiscal_rule_tmpl_res_country_to_rel',
                    id1='rule_id', id2='country_id',
                    string='Destination Countries'),
                'to_state_ids' : fields.many2many(
                            'res.country.state',
                            rel='account_fiscal_rule_tmpl_state_to_rel',
                            id1='rule_id', id2='state_id',
                            string='Destination States'),
                'fiscal_position_id': fields.many2one('account.fiscal.position.template', 'Fiscal Position', required=True),
                'use_sale': fields.boolean('Use in sales order'),
                'use_invoice': fields.boolean('Use in Invoices'),
                'use_purchase': fields.boolean('Use in Purchases'),
                'use_picking': fields.boolean('Use in Picking'),
                'date_start': fields.date('Start Date', help="Starting date for this rule to be valid."),
                'date_end': fields.date('End Date', help="Ending date for this rule to be valid."),
                'sequence': fields.integer(
                    'Priority', required=True,
                    help='The lowest number will be applied.'),
                }

    _defaults = {
        'sequence': 10,
    }

    def init(self, cr):
        # migration from previous version
        # to_country as a m2o becomes to_country_ids as a m2m
        # and so on for from_country, from_state, to_state
        cr.execute("SELECT column_name FROM information_schema.columns "
                   "WHERE table_name = 'account_fiscal_position_rule_template' "
                   "AND column_name = 'to_country'")
        if cr.fetchone():
            migrations = [
            {'rel_table': 'account_fiscal_rule_tmpl_res_country_to_rel',
             'from_field': 'to_country',
             'rel_field': 'country_id'},
            {'rel_table': 'account_fiscal_rule_tmpl_state_to_rel',
             'from_field': 'to_state',
             'rel_field': 'state_id'},
            {'rel_table': 'account_fiscal_rule_tmpl_res_country_from_rel',
             'from_field': 'from_country',
             'rel_field': 'country_id'},
            {'rel_table': 'account_fiscal_rule_tmpl_state_from_rel',
             'from_field': 'from_state',
             'rel_field': 'state_id'}]
            for migration in migrations:
                cr.execute("INSERT INTO %(rel_table)s "
                           "(rule_id, %(rel_field)s) "
                           "(SELECT id, %(from_field)s FROM "
                           " account_fiscal_position_rule_template "
                           "WHERE %(from_field)s IS NOT NULL "
                           " AND (id, %(from_field)s) NOT IN "
                           " (SELECT rule_id, %(rel_field)s "
                           "  FROM %(rel_table)s))" % migration)

                cr.execute("UPDATE account_fiscal_position_rule_template "
                           "SET %(from_field)s = NULL" % migration)

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

        vals = {'name': template.name,
                'description': template.description,
                'company_id': company_id,
                'fiscal_position_id': fiscal_position_ids[0],
                'use_sale': template.use_sale,
                'use_invoice': template.use_invoice,
                'use_purchase': template.use_purchase,
                'use_picking': template.use_picking,
                'date_start': template.date_start,
                'date_end': template.date_end,
                'sequence': template.sequence, }

        # copy many2many fields from the template
        m2m_fields = ['to_country_ids', 'from_country_ids',
                      'to_state_ids', 'from_state_ids']
        for field in m2m_fields:
            field_ids = [item.id for item in getattr(template, field)]
            if field_ids:
                vals[field] = [(6, 0, field_ids)]

        return vals

    def action_create(self, cr, uid, ids, context=None):

        obj_wizard = self.browse(cr, uid, ids[0], context=context)

        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        obj_fiscal_position_rule_template = self.pool.get('account.fiscal.position.rule.template')
        obj_fiscal_position = self.pool.get('account.fiscal.position')

        company_id = obj_wizard.company_id.id

        pfr_ids = obj_fiscal_position_rule_template.search(
            cr, uid, [], context=context)

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
