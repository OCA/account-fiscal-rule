# © 2014 -2024 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    is_ecotax = fields.Boolean(
        "Ecotax",
        help="Warning : To include Ecotax "
        "in the VAT tax check this :\n"
        '1: check  "included in base amount "\n'
        "2: The Ecotax sequence must be less then "
        "VAT tax (in sale)",
    )

    @api.onchange("is_ecotax")
    def onchange_is_ecotax(self):
        if self.is_ecotax:
            self.amount_type = "fixed"
            self.amount = 0.0
            self.include_base_amount = True

    def _add_tax_details_in_base_line(self, base_line, company, rounding_method=None):
        """Inject the ecotax amounts into the tax engine.

        An ecotax tax is a simple fixed-amount template: its real amount is
        never its static ``amount`` field (kept at 0) but the sum of the
        ecotax lines of the document line, which is the single source of
        truth (fixed, weight-based and forced amounts, filtered by delivery
        country and by any other eligibility rule). This avoids generating
        one account.tax per ecotax amount.

        The amounts are injected through the native ``manual_tax_amounts``
        mechanism before the standard computation, so the sequential engine
        handles them natively: ``include_base_amount`` propagation (ecotax
        included in the VAT base), totals, rounding and tax line creation
        all stay consistent.
        """
        ecotax_taxes = base_line["tax_ids"].filtered(lambda tax: tax.is_ecotax)
        if ecotax_taxes:
            manual_tax_amounts = base_line.get("manual_tax_amounts") or {}
            for tax in ecotax_taxes:
                if str(tax.id) in manual_tax_amounts:
                    # respect amounts manually encoded on the invoice tax line
                    continue
                amount_currency = tax._get_ecotax_tax_amount_currency(base_line)
                if amount_currency is not None:
                    manual_tax_amounts[str(tax.id)] = {
                        "tax_amount_currency": amount_currency
                    }
            if manual_tax_amounts:
                base_line["manual_tax_amounts"] = manual_tax_amounts
        return super()._add_tax_details_in_base_line(
            base_line, company, rounding_method
        )

    def _get_ecotax_tax_amount_currency(self, base_line):
        """Return the ecotax amount for this tax, in the base line currency.

        The ecotax lines of the document line are the single source of truth.
        A document line without ecotax line carries no ecotax at all: the
        amount is zero even if the product is ecotax eligible.

        When the computation is not made on a stored document line (e.g. the
        legacy ``compute_all`` API, used by the point of sale or by other
        modules), there is no ecotax line to read: ``None`` is returned and
        no amount is injected, so the tax keeps its static amount.
        """
        self.ensure_one()
        record = base_line.get("record")
        if record is None or not hasattr(record, "ecotax_line_ids"):
            return None
        # amount_total is expressed in the document line currency
        return sum(
            record.ecotax_line_ids.filtered(
                lambda line: self in line.classification_id._get_ecotax_taxes()
            ).mapped("amount_total")
        )
