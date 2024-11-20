# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, exceptions, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    ecotax_move_id = fields.Many2one("account.move", readonly=True, copy=False)

    def _create_prepare_ecotax_move_vals(self):
        self.ensure_one()
        ecotax_journal_id = self.company_id.ecotax_journal_id.id
        if not ecotax_journal_id:
            raise exceptions.UserError(
                _(
                    "Please configure the relative ecotax journal on the company settings"
                )
            )
        return {
            "journal_id": ecotax_journal_id,
            "move_type": "entry",
            "ref": _("Ecotaxe entry for %s") % self.name,
            "date": self.date,
            "currency_id": self.currency_id.id,
            "company_id": self.company_id.id,
        }

    def _manage_ecotax_isolation(self):
        self.ensure_one()
        ecotax_lines = self.invoice_line_ids.ecotax_line_ids
        account_ecotax_mapping = defaultdict(float)
        product_account_mapping = defaultdict(float)
        for ecotax_line in ecotax_lines:
            account = (
                ecotax_line.classification_id.ecotax_account_id
                or self.company_id.ecotax_account_id
            )
            if not account:
                continue
            account_ecotax_mapping[account] += ecotax_line.amount_total
            product_account_mapping[
                ecotax_line.account_move_line_id.account_id
            ] += ecotax_line.amount_total
        if not account_ecotax_mapping:
            return self.env["account.move"]
        ecotax_move = self.ecotax_move_id
        if ecotax_move:
            if ecotax_move.state != "cancel":
                raise exceptions.ValidationError(
                    _("The linked ecotax entry should be canceled.")
                )
            ecotax_move.button_draft()
            ecotax_move.line_ids.unlink()
        else:
            vals = self._create_prepare_ecotax_move_vals()
            ecotax_move = self.create(vals)
            self.write({"ecotax_move_id": ecotax_move.id})
        line_vals_list = []
        for account, amount_curr in account_ecotax_mapping.items():
            line_vals = {
                "name": "ecotax for %s" % self.name,
                "account_id": account.id,
                "currency_id": self.currency_id.id,
                "amount_currency": self.move_type == "out_invoice"
                and -amount_curr
                or amount_curr,
                "move_id": ecotax_move.id,
                # We never want tax lines here even if the account has a default
                # tax set
                "tax_ids": False,
            }
            line_vals_list.append(line_vals)
        for account, amount_curr in product_account_mapping.items():
            line_vals = {
                "account_id": account.id,
                "currency_id": self.currency_id.id,
                "amount_currency": self.move_type == "out_invoice"
                and amount_curr
                or -amount_curr,
                "move_id": ecotax_move.id,
                # We never want tax lines here even if the account has a default
                # tax set
                "tax_ids": False,
            }
            line_vals_list.append(line_vals)
        ecotax_move.write({"line_ids": [(0, 0, vals) for vals in line_vals_list]})
        ecotax_move.action_post()
        return ecotax_move

    def _post(self, soft=True):
        res = super()._post(soft=soft)
        for move in self:
            if move.move_type in ("out_invoice", "out_refund"):
                move._manage_ecotax_isolation()
        return res

    def button_draft(self):
        res = super().button_draft()
        if self.ecotax_move_id:
            self.ecotax_move_id.button_cancel()
        return res

    def button_cancel(self):
        res = super().button_cancel()
        if self.ecotax_move_id:
            self.ecotax_move_id.button_cancel()
        return res
