from odoo import models
from odoo.tools import float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _avatax_compute_tax(self):
        """Contact REST API and recompute taxes for a Sale Order."""
        self and self.ensure_one()
        doc_type = self._get_avatax_doc_type()
        Tax = self.env["account.tax"]
        avatax_config = self.company_id.get_avatax_config_company()
        if not avatax_config:
            return False

        partner = self.partner_id
        if avatax_config.use_partner_invoice_id:
            partner = self.partner_invoice_id

        taxable_lines = self._avatax_prepare_lines(self.order_line)
        tax_result = avatax_config.create_transaction(
            self.date_order,
            self.name,
            doc_type,
            partner,
            self.warehouse_id.partner_id or self.company_id.partner_id,
            self.tax_address_id or self.partner_id,
            taxable_lines,
            self.user_id,
            self.exemption_code or None,
            self.exemption_code_id.code or None,
            currency_id=self.currency_id,
            log_to_record=self,
        )

        tax_result_lines = {int(x["lineNumber"]): x for x in tax_result["lines"]}

        if avatax_config.avatax_group_lines and len(tax_result_lines) == 1:
            single_result_line = list(tax_result_lines.values())[0]

            total_tax = (
                single_result_line.get("taxCalculated")
                or single_result_line.get("tax")
                or 0.0
            )

            order_lines = self.order_line.filtered(lambda l: not l.display_type)
            if not order_lines or not total_tax:
                self.tax_amount = tax_result.get("totalTax")
                return True

            def _line_base(line):
                return (
                    line.price_unit
                    * line.product_uom_qty
                    * (1 - (line.discount or 0.0) / 100.0)
                )

            total_base = sum(_line_base(line) for line in order_lines)
            if not total_base:
                self.tax_amount = tax_result.get("totalTax")
                return True

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
            line_count = len(order_lines)

            for idx, line in enumerate(order_lines, start=1):
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

                if tax_line not in line.tax_id:
                    line_taxes = (
                        tax_line
                        if avatax_config.override_line_taxes
                        else tax_line | line.tax_id.filtered(lambda x: not x.is_avatax)
                    )
                    line.tax_id = line_taxes

                line.tax_amt = line_tax

            self.tax_amount = tax_result.get("totalTax")
            return True

        for line in self.order_line:
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
                tax, line = self.update_tax_details(tax, line, tax_result_line)
                if tax not in line.tax_id:
                    line_taxes = (
                        tax
                        if avatax_config.override_line_taxes
                        else tax | line.tax_id.filtered(lambda x: not x.is_avatax)
                    )
                    line.tax_id = line_taxes
                line.tax_amt = tax_result_line["tax"]

        self.tax_amount = tax_result.get("totalTax")
        return True
