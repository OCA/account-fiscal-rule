# © 2014 -2024 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveLineEcotax(models.Model):
    """Keep the tax lines in sync with the ecotax amount of the line.

    The tax engine reads the ecotax amount from these lines, but they live in
    a dedicated model: editing them changes none of the fields
    ``account.move._sync_tax_lines`` watches on the base lines (``price_unit``,
    ``quantity``, ``discount``, grouping key), so the tax lines are left on
    the previous amount.
    """

    _inherit = "account.move.line.ecotax"

    def write(self, vals):
        res = super().write(vals)
        if {"classification_id", "force_amount_unit"} & set(vals):
            for move in self.account_move_line_id.move_id.filtered(
                lambda move: move.state == "draft"
                and move.is_sale_document(include_receipts=True)
            ):
                self._recompute_tax_lines(move)
        return res

    def _recompute_tax_lines(self, move):
        """Recompute the tax lines of ``move``, the way ``_sync_tax_lines``
        does it when a base line has been modified (``round_from_tax_lines``
        is False): the ecotax tax line and the VAT computed on top of it
        (``include_base_amount``) follow the new amount.

        The existing tax lines are updated or deleted and the missing ones
        created, as ``_sync_tax_lines`` does: dropping them all and creating
        them again would break the other synchronizers, which still hold
        references to them while ``account.move.write`` is running.
        """
        AccountTax = self.env["account.tax"]
        AccountMoveLine = self.env["account.move.line"]
        base_lines, tax_lines = move._get_rounded_base_and_tax_lines(
            round_from_tax_lines=False
        )
        AccountTax._add_accounting_data_in_base_lines_tax_details(
            base_lines, move.company_id, include_caba_tags=move.always_tax_exigible
        )
        tax_results = AccountTax._prepare_tax_lines(
            base_lines, move.company_id, tax_lines=tax_lines
        )
        for base_line, to_update in tax_results["base_lines_to_update"]:
            base_line["record"].write(to_update)  # no-op when unchanged
        to_delete = AccountMoveLine
        for values in tax_results["tax_lines_to_delete"]:
            to_delete |= values["record"]
        if to_delete:
            to_delete.with_context(dynamic_unlink=True).unlink()
        if tax_results["tax_lines_to_add"]:
            AccountMoveLine.create(
                [
                    dict(values, display_type="tax", move_id=move.id)
                    for values in tax_results["tax_lines_to_add"]
                ]
            )
        for values, _grouping_key, to_update in tax_results["tax_lines_to_update"]:
            values["record"].write(to_update)  # no-op when unchanged
