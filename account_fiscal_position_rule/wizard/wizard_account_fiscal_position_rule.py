# Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Renato Lima <renato.lima@akretion.com>
# Copyright 2012-TODAY Camptocamp SA
#   @author: Guewen Baconnier
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class WizardAccountFiscalPositionRule(models.TransientModel):
    _name = "wizard.account.fiscal.position.rule"
    _description = "Account Fiscal Position Rule Wizard"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env["res.company"]._company_default_get(
            "wizard.account.fiscal.position.rule"
        ),
    )

    def _template_vals(self, template, company_id, fiscal_position_id):
        return {
            "name": template.name,
            "description": template.description,
            "from_country_group_id": template.from_country_group_id.id,
            "from_country": template.from_country.id,
            "from_state": template.from_state.id,
            "to_invoice_country_group_id": template.to_invoice_country_group_id.id,
            "to_invoice_country": template.to_invoice_country.id,
            "to_invoice_state": template.to_invoice_state.id,
            "to_shipping_country_group_id": template.to_shipping_country_group_id.id,
            "to_shipping_country": template.to_shipping_country.id,
            "to_shipping_state": template.to_shipping_state.id,
            "company_id": company_id,
            "fiscal_position_id": fiscal_position_id,
            "use_sale": template.use_sale,
            "use_invoice": template.use_invoice,
            "use_purchase": template.use_purchase,
            "use_picking": template.use_picking,
            "date_start": template.date_start,
            "date_end": template.date_end,
            "sequence": template.sequence,
            "vat_rule": template.vat_rule,
        }

    def action_create(self):
        obj_fpr_temp = self.env["account.fiscal.position.rule.template"]
        company_id = self.company_id.id

        fsc_rule_template = obj_fpr_temp.search([])
        # TODO fix me doesn't work multi template that have empty fiscal
        # position maybe we should link the rule with the account template
        for fpr_template in fsc_rule_template:
            fp_ids = False
            if fpr_template.fiscal_position_id:
                fp_ids = self.env["account.fiscal.position"].search(
                    [("name", "=", fpr_template.fiscal_position_id.name)]
                )
                if not fp_ids:
                    continue
            values = self._template_vals(fpr_template, company_id, fp_ids[0].id)
            self.env["account.fiscal.position.rule"].create(values)
        return True
