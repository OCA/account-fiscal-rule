# -*- coding: utf-8 -*-
# Copyright (C) 2014 -Today Akretion (http://www.akretion.com)
#   @author Renato Lima (https://twitter.com/renatonlima)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class WizardAccountProductFiscalClassification(models.TransientModel):
    """Wizard to create fiscal classification based in fiscal classification
    template."""
    _name = 'wizard.account.product.fiscal.classification'

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'account.invoice'))

    @api.multi
    def action_create(self):
        obj_tax = self.env['account.tax']
        obj_tax_template = self.env['account.tax.template']
        obj_fc = self.env['account.product.fiscal.classification']
        obj_fc_template = self.env[
            'account.product.fiscal.classification.template']

        def map_taxes(taxes):
            tax_ids = []
            for tax in taxes:
                for company in companies:
                    if company_taxes[company].get(tax.id):
                        tax_ids.append(company_taxes[company][tax.id])
            return tax_ids

        company_id = self.company_id.id
        companies = []

        if company_id:
            companies.append(company_id)
        else:
            companies = self.env['res.company'].sudo().search([]).ids

        company_taxes = {}
        for company in companies:
            company_taxes[company] = {}
            for tax in obj_tax.sudo().search([('company_id', '=', company)]):
                tax_template = obj_tax_template.search(
                    [('name', '=', tax.name)])

                if tax_template:
                    company_taxes[company][tax_template[0].id] = tax.id

        for fclass_template in obj_fc_template.search([]):

            fclass_id = obj_fc.search(
                [('name', '=', fclass_template.name)])

            if not fclass_id:
                sale_tax_ids = map_taxes(fclass_template.sale_tax_ids)
                purchase_tax_ids = map_taxes(fclass_template.purchase_tax_ids)

                vals = {
                    'active': fclass_template.active,
                    'code': fclass_template.code,
                    'name': fclass_template.name,
                    'description': fclass_template.description,
                    'company_id': company_id,
                    'sale_tax_ids': [(6, 0, sale_tax_ids)],
                    'purchase_tax_ids': [(6, 0, purchase_tax_ids)],
                }
                obj_fc.sudo().create(vals)

        return True
