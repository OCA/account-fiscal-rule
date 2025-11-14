import logging

from odoo import fields, models
from odoo.tools import float_compare, float_round

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _avatax_compute_tax(self, commit=False):
        """Contact REST API and recompute taxes for an Invoice."""
        self and self.ensure_one()
        avatax_config = self.company_id.get_avatax_config_company()
        if not avatax_config:
            # Skip Avatax computation if no configuration is found
            return

        doc_type = self._get_avatax_doc_type(commit=commit)
        tax_date = self.get_origin_tax_date() or self.invoice_date
        taxable_lines = self._avatax_prepare_lines(doc_type)

        tax_result = avatax_config.create_transaction(
            self.invoice_date or fields.Date.today(),
            self.name,
            doc_type,
            (
                self.so_partner_id
                if self.so_partner_id and avatax_config.use_so_partner_id
                else self.partner_id
            ),
            self.warehouse_id.partner_id or self.company_id.partner_id,
            self.tax_address_id or self.partner_id,
            taxable_lines,
            self.user_id,
            self.exemption_code or None,
            self.exemption_code_id.code or None,
            commit,
            tax_date,
            # TODO: can we report self.invoice_doc_no?
            self.name if self.move_type == "out_refund" else "",
            self.location_code or "",
            is_override=self.move_type == "out_refund",
            currency_id=self.currency_id,
            ignore_error=300 if commit else None,
            log_to_record=self,
        )

        # If committing, and document exists, try unvoiding it
        # Error number 300 = GetTaxError, Expected Saved|Posted
        if commit and tax_result.get("number") == 300:
            _logger.info(
                "Document %s (%s) already exists in Avatax. "
                "Should be a voided transaction. "
                "Unvoiding and re-committing.",
                self.name,
                doc_type,
            )
            avatax_config.unvoid_transaction(self.name, doc_type)
            avatax_config.commit_transaction(self.name, doc_type)
            return tax_result

        if self.state == "draft":
            Tax = self.env["account.tax"]
            tax_result_lines = {int(x["lineNumber"]): x for x in tax_result["lines"]}
            taxes_to_set = {}

           
            if avatax_config.avatax_group_lines and len(tax_result_lines) == 1:
                single_result_line = list(tax_result_lines.values())[0]

                total_tax = (
                    single_result_line.get("taxCalculated")
                    or single_result_line.get("tax")
                    or 0.0
                )

                inv_lines = self.invoice_line_ids.filtered(
                    lambda l: not l.display_type
                )
                if inv_lines and total_tax:
                    def _line_base(line):
                        amount = line._get_avatax_amount()
                        if line.quantity < 0:
                            amount = -amount
                        return amount

                    total_base = sum(_line_base(l) for l in inv_lines)

                    if total_base:
                        tax_calculation = 0.0
                        if single_result_line.get("taxableAmount"):
                            tax_calculation = (
                                single_result_line["taxCalculated"]
                                / single_result_line["taxableAmount"]
                            )
                        rate = round(tax_calculation * 100, 4)
                        tax = Tax.get_avalara_tax(rate, doc_type)

                        remaining_tax = total_tax
                        currency = self.currency_id
                        line_count = len(inv_lines)

                        for idx, line in enumerate(inv_lines, start=1):
                            base = _line_base(line)

                            if idx == line_count:
                                line_tax = remaining_tax
                            else:
                                share = base / total_base if total_base else 0.0
                                line_tax = float_round(
                                    total_tax * share,
                                    precision_rounding=currency.rounding,
                                )
                                remaining_tax -= line_tax

                            tax_line, line_obj = self.update_tax_details(
                                tax, line, single_result_line
                            )

                            if tax_line:
                                base_taxes = line.tax_ids.filtered(
                                    lambda x: not x.is_avatax
                                )
                                if avatax_config.override_line_taxes:
                                    taxes_to_set[line.id] = tax_line
                                else:
                                    taxes_to_set[line.id] = base_taxes | tax_line

                            line.avatax_amt_line = line_tax            
            else:
                for line in self.invoice_line_ids:
                    tax_result_line = tax_result_lines.get(line.id)
                    if tax_result_line:
                        tax_calculation = 0.0
                        if tax_result_line["taxableAmount"]:
                            tax_calculation = (
                                tax_result_line["taxCalculated"]
                                / tax_result_line["taxableAmount"]
                            )
                        rate = round(tax_calculation * 100, 4)
                        tax = Tax.get_avalara_tax(rate, doc_type)
                        tax, line = self.update_tax_details(
                            tax, line, tax_result_line
                        )
                        if tax and tax not in line.tax_ids:
                            line_taxes = line.tax_ids.filtered(
                                lambda x: not x.is_avatax
                            )
                            taxes_to_set[line.id] = line_taxes | tax
                        line.avatax_amt_line = tax_result_line["tax"]

            self.with_context(check_move_validity=False).avatax_amount = tax_result[
                "totalTax"
            ]
            container = {"records": self}
            
            with self.with_context(
                avatax_invoice=self, check_move_validity=False
            )._sync_dynamic_lines(container), self.line_ids.mapped(
                "move_id"
            )._check_balanced(
                container
            ):
                for line_id in taxes_to_set.keys():
                    line = self.invoice_line_ids.filtered(lambda x: x.id == line_id)
                    line.write({"tax_ids": [(6, 0, [])]})
                    line.with_context(
                        avatax_invoice=self, check_move_validity=False
                    ).write({"tax_ids": taxes_to_set.get(line_id).ids})

            self._compute_amount()

            if float_compare(
                self.amount_untaxed + max(self.amount_tax, abs(self.avatax_amount)),
                self.amount_residual,
                precision_rounding=self.currency_id.rounding or 0.001,
            ):
                taxes_data = {
                    iline.id: iline.tax_ids for iline in self.invoice_line_ids
                }
                self.invoice_line_ids.write({"tax_ids": [(6, 0, [])]})
                for line in self.invoice_line_ids:
                    line.write({"tax_ids": taxes_data[line.id].ids})

        return tax_result
