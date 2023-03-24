# Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#   @author Renato Lima <renato.lima@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    fiscal_position_rule_ids = fields.One2many(
        comodel_name="account.fiscal.position.rule",
        inverse_name="fiscal_position_id",
        string="Fiscal Position Rules",
        readonly=True,
    )
    fiscal_position_rule_count = fields.Integer(
        compute="_compute_fiscal_position_rule_count"
    )

    @api.model
    def get_fiscal_position(self, partner_id, delivery_id=None):
        fp = super(AccountFiscalPosition, self).get_fiscal_position(
            partner_id, delivery_id
        )
        if fp:
            return fp
        if partner_id and delivery_id:
            fiscal_rule = self.env["account.fiscal.position.rule"]
            kwargs = {
                "company_id": self.env.company,
                "partner_id": self.env["res.partner"].browse(partner_id),
                "partner_invoice_id": self.env["res.partner"].browse(partner_id),
                "partner_shipping_id": self.env["res.partner"].browse(delivery_id),
            }
            fp = fiscal_rule.apply_fiscal_mapping(**kwargs)
        return fp and fp.id or False

    def _compute_fiscal_position_rule_count(self):
        for fpos in self:
            fpos.fiscal_position_rule_count = len(fpos.fiscal_position_rule_ids)

    def action_fiscal_position_rules(self):
        self.ensure_one()
        fpos_rules = self.fiscal_position_rule_ids
        action = self.env.ref(
            "account_fiscal_position_rule.action_account_fiscal_position_rule_form"
        ).read()[0]
        if len(fpos_rules) > 1:
            action["domain"] = [("id", "in", fpos_rules.ids)]
        elif len(fpos_rules) == 1:
            form_view = [
                (
                    self.env.ref(
                        "account_fiscal_position_rule.view_account_fiscal_position_rule_form"
                    ).id,
                    "form",
                )
            ]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = fpos_rules.ids[0]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action
