# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    amount_ecotax = fields.Float(
        digits="Ecotax",
        string="Included Ecotax",
        store=True,
        compute="_compute_ecotax",
    )

    @api.depends("invoice_line_ids.subtotal_ecotax")
    def _compute_ecotax(self):
        for move in self:
            move.amount_ecotax = sum(move.line_ids.mapped("subtotal_ecotax"))

    @api.model
    def _get_tax_totals(
        self, partner, tax_lines_data, amount_total, amount_untaxed, currency
    ):
        """Include Ecotax when this method is called upon a single invoice

        NB: `_get_tax_totals()` is called when field `tax_totals_json` is
        computed, which is used in invoice form view to display taxes and
        totals.
        """
        res = super()._get_tax_totals(
            partner, tax_lines_data, amount_total, amount_untaxed, currency
        )
        if len(self) != 1:
            return res

        base_amt = self.amount_total
        ecotax_amt = self.amount_ecotax
        if not ecotax_amt:
            return res

        env = self.with_context(lang=partner.lang).env
        fmt_ecotax_amt = formatLang(env, ecotax_amt, currency_obj=currency)
        fmt_base_amt = formatLang(env, base_amt, currency_obj=currency)
        data = list(res["groups_by_subtotal"].get(_("Untaxed Amount")) or [])
        data.append(
            {
                "tax_group_name": _("Included Ecotax"),
                "tax_group_amount": ecotax_amt,
                "formatted_tax_group_amount": fmt_ecotax_amt,
                "tax_group_base_amount": base_amt,
                "formatted_tax_group_base_amount": fmt_base_amt,
                "tax_group_id": False,  # Not an actual tax
                "group_key": "Included Ecotax",
            }
        )
        res["groups_by_subtotal"][_("Untaxed Amount")] = data
        return res
