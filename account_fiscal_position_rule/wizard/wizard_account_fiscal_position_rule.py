# -*- coding: utf-8 -*-
# Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Renato Lima <renato.lima@akretion.com>
# Copyright 2012-TODAY Camptocamp SA
#   @author: Guewen Baconnier
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import time

from odoo import models, fields, api


class AccountFiscalPositionRuleTemplate(models.Model):
    _name = 'account.fiscal.position.rule.template'
    _description = 'Account Fiscal Position Rule Template'
    _order = 'sequence'

    name = fields.Char(
        string='Name',
        required=True)

    description = fields.Char(
        string='Description')

    from_country = fields.Many2one(
        comodel_name='res.country',
        string='Country Form')

    from_state = fields.Many2one(
        comodel_name='res.country.state',
        string='State From',
        domain="[('country_id','=',from_country)]")

    to_invoice_country = fields.Many2one(
        comodel_name='res.country',
        string='Country To')

    to_invoice_state = fields.Many2one(
        comodel_name='res.country.state',
        string='State To',
        domain="[('country_id','=',to_invoice_country)]")

    to_shipping_country = fields.Many2one(
        comodel_name='res.country',
        string='Destination Country')

    to_shipping_state = fields.Many2one(
        comodel_name='res.country.state',
        string='Destination State',
        domain="[('country_id','=',to_shipping_country)]")

    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position.template',
        string='Fiscal Position',
        required=True)

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
        default='both',
        help=('Choose if the customer need to have the'
              ' field VAT fill for using this fiscal position'))


class WizardAccountFiscalPositionRule(models.TransientModel):
    _name = 'wizard.account.fiscal.position.rule'
    _description = 'Account Fiscal Position Rule Wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'wizard.account.fiscal.position.rule'))

    @api.multi
    def _template_vals(self, template, company_id, fiscal_position_id):
        return {
            'name': template.name,
            'description': template.description,
            'from_country': template.from_country.id,
            'from_state': template.from_state.id,
            'to_invoice_country': template.to_invoice_country.id,
            'to_invoice_state': template.to_invoice_state.id,
            'to_shipping_country': template.to_shipping_country.id,
            'to_shipping_state': template.to_shipping_state.id,
            'company_id': company_id,
            'fiscal_position_id': fiscal_position_id,
            'use_sale': template.use_sale,
            'use_invoice': template.use_invoice,
            'use_purchase': template.use_purchase,
            'use_picking': template.use_picking,
            'date_start': template.date_start,
            'date_end': template.date_end,
            'sequence': template.sequence,
            'vat_rule': template.vat_rule,
        }

    @api.multi
    def action_create(self):
        obj_fpr_temp = self.env['account.fiscal.position.rule.template']
        company_id = self.company_id.id

        fsc_rule_template = obj_fpr_temp.search([])
        # TODO fix me doesn't work multi template that have empty fiscal
        # position maybe we should link the rule with the account template
        for fpr_template in fsc_rule_template:
            fp_ids = False
            if fpr_template.fiscal_position_id:
                fp_ids = self.env['account.fiscal.position'].search(
                    [('name', '=', fpr_template.fiscal_position_id.name)])
                if not fp_ids:
                    continue
            values = self._template_vals(
                fpr_template, company_id, fp_ids[0].id)
            self.env['account.fiscal.position.rule'].create(values)
        return True
