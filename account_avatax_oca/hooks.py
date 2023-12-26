# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api
from odoo.tools import frozendict

from odoo.addons.account.models.account_move_line import AccountMoveLine


def pre_init_hook(cr):
    # Preserve key data when moving from account_avatax to account_avatax_oca
    # The process is to first install account_avatax_oca
    # and then uninstall account_avatax
    cr.execute(
        """
        UPDATE ir_model_data
        SET module = 'account_avatax_oca'
        WHERE name in ('avatax_fiscal_position_us', 'account_avatax')
    """
    )


def post_load_hook():  # noqa: C901
    @api.depends(
        "tax_ids",
        "currency_id",
        "partner_id",
        "analytic_distribution",
        "balance",
        "partner_id",
        "move_id.partner_id",
        "price_unit",
        "quantity",
    )
    def _compute_all_tax_new(self):
        for line in self:
            sign = line.move_id.direction_sign
            if line.display_type == "tax":
                line.compute_all_tax = {}
                line.compute_all_tax_dirty = False
                continue
            if line.display_type == "product" and line.move_id.is_invoice(True):
                amount_currency = sign * line.price_unit * (1 - line.discount / 100)
                handle_price_include = True
                quantity = line.quantity
            else:
                amount_currency = line.amount_currency
                handle_price_include = False
                quantity = 1
            compute_all_currency = line.tax_ids.with_context(
                current_aml=line.id
            ).compute_all(
                amount_currency,
                currency=line.currency_id,
                quantity=quantity,
                product=line.product_id,
                partner=line.move_id.partner_id or line.partner_id,
                is_refund=line.is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=line.move_id.always_tax_exigible,
                fixed_multiplicator=sign,
            )
            rate = line.amount_currency / line.balance if line.balance else 1
            line.compute_all_tax_dirty = True
            line.compute_all_tax = {
                frozendict(
                    {
                        "tax_repartition_line_id": tax["tax_repartition_line_id"],
                        "group_tax_id": tax["group"] and tax["group"].id or False,
                        "account_id": tax["account_id"] or line.account_id.id,
                        "currency_id": line.currency_id.id,
                        "analytic_distribution": (
                            (tax["analytic"] or not tax["use_in_tax_closing"])
                            and line.move_id.state == "draft"
                        )
                        and line.analytic_distribution,
                        "tax_ids": [(6, 0, tax["tax_ids"])],
                        "tax_tag_ids": [(6, 0, tax["tag_ids"])],
                        "partner_id": line.move_id.partner_id.id or line.partner_id.id,
                        "move_id": line.move_id.id,
                        "display_type": line.display_type,
                    }
                ): {
                    "name": tax["name"]
                    + (" " + _("(Discount)") if line.display_type == "epd" else ""),
                    "balance": tax["amount"] / rate,
                    "amount_currency": tax["amount"],
                    "tax_base_amount": tax["base"]
                    / rate
                    * (-1 if line.tax_tag_invert else 1),
                }
                for tax in compute_all_currency["taxes"]
                if tax["amount"]
            }
            if not line.tax_repartition_line_id:
                line.compute_all_tax[frozendict({"id": line.id})] = {
                    "tax_tag_ids": [(6, 0, compute_all_currency["base_tags"])],
                }

    if not hasattr(AccountMoveLine, "_compute_all_tax_origin"):
        AccountMoveLine._compute_all_tax_origin = AccountMoveLine._compute_all_tax
    AccountMoveLine._compute_all_tax = _compute_all_tax_new
