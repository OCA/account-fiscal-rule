from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _avatax_prepare_line(self, sign=1, doc_type=None):
        """
        Prepare invoice line data for Avatax.

        When company.avatax_group_lines is enabled, only the first invoice line
        of the move will produce a dict, aggregating the amounts of all lines.
        All other lines will return {} so they are ignored in the Avatax payload.
        """
        move = self.move_id
        company = move.company_id

        if company and getattr(company, "avatax_group_lines", False):
            first_line = move.invoice_line_ids[:1]
            if not first_line or self != first_line[0]:
                return {}

            total_amount = 0.0
            for line in move.invoice_line_ids:
                amount = sign * line._get_avatax_amount()
                if hasattr(line, "quantity") and line.quantity < 0:
                    amount = -amount
                total_amount += amount

            line = first_line[0]
            product = line.product_id

            item_code = None
            tax_code = None
            upc_enable = False
            avatax_config = None

            if hasattr(company, "get_avatax_config_company"):
                avatax_config = company.get_avatax_config_company()
                if avatax_config:
                    upc_enable = bool(getattr(avatax_config, "upc_enable", False))

            if product:
                if product.barcode and upc_enable:
                    item_code = "UPC:%s" % product.barcode
                else:
                    item_code = product.default_code or "ID:%d" % product.id
                tax_code = product.applicable_tax_code_id.name

            if not item_code:
                item_code = "DOC:%s" % (move.name or move.ref or move.id)
            description = line.name or move.name or "Combined Items"

            return {
                "qty": 1,
                "itemcode": item_code,
                "description": description,
                "amount": total_amount,
                "tax_code": tax_code,
                "id": line,
                "account_id": line.account_id.id,
                "tax_id": line.tax_ids,
            }

        return super()._avatax_prepare_line(sign=sign, doc_type=doc_type)
