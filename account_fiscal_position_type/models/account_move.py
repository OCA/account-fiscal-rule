# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression


class AccountMove(models.Model):
    _inherit = "account.move"

    suitable_fiscal_position_ids = fields.Many2many(
        "account.fiscal.position",
        compute="_compute_suitable_journal_ids",
    )

    fiscal_position_id = fields.Many2one(
        domain="[('id', 'in', suitable_fiscal_position_ids)]",
    )

    @api.onchange("fiscal_position_id", "suitable_fiscal_position_ids")
    def _onchange_partner_id_suitable_fiscal_position_ids(self):
        if self.fiscal_position_id.id not in self.suitable_fiscal_position_ids.ids:
            self.fiscal_position_id = False

    @api.depends("company_id", "invoice_filter_type_domain")
    def _compute_suitable_journal_ids(self):
        res = super()._compute_suitable_journal_ids()
        for m in self:
            domain = [("company_id", "=", self.env.company.id)]
            if m.invoice_filter_type_domain in ["sale", "purchase"]:
                domain = expression.AND(
                    [
                        [
                            (
                                "type_position_use",
                                "in",
                                [m.invoice_filter_type_domain, "all"],
                            )
                        ],
                        domain,
                    ]
                )
            m.suitable_fiscal_position_ids = self.env["account.fiscal.position"].search(
                domain
            )
        return res
