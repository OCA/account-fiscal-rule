# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    product_domain = fields.Char(
        string="Product filter",
        help="Select the product domain for applying the fiscal position. Keep empty "
        "for all.",
        default="[]",
    )

    def map_tax(self, taxes):
        template = self.env.context.get("fp_template")
        if not template:
            return super().map_tax(taxes)
        tax_lines_by_src = defaultdict(lambda: self.env["account.fiscal.position.tax"])
        for line in self.tax_ids.filtered(
            lambda line: line._is_applicable_to_product_template(template)
        ):
            tax_lines_by_src[line.tax_src_id.id] |= line
        mapped_taxes = self.env["account.tax"]
        for tax in taxes:
            tax_lines = tax_lines_by_src[tax.id]
            if tax_lines:
                mapped_taxes |= tax_lines.filtered("tax_dest_active").tax_dest_id
            else:
                mapped_taxes |= tax
        return mapped_taxes

    @api.model
    def _template_matches_product_domain(self, template, product_domain):
        return bool(template.filtered_domain(safe_eval(product_domain)))

    def _has_product_domain(self):
        return bool(safe_eval(self.product_domain or "[]"))

    def write(self, vals):
        had_product_domain = {}
        if "product_domain" in vals:
            had_product_domain = {fpos.id: fpos._has_product_domain() for fpos in self}
        res = super().write(vals)
        if "product_domain" in vals:
            for fpos in self.filtered("tax_ids"):
                has_product_domain = fpos._has_product_domain()
                if not had_product_domain[fpos.id] and has_product_domain:
                    fpos.tax_ids.apply_product_domain = "included"
                elif had_product_domain[fpos.id] and not has_product_domain:
                    fpos.tax_ids.apply_product_domain = False
        return res


class AccountFiscalPositionTax(models.Model):
    _inherit = "account.fiscal.position.tax"

    apply_product_domain = fields.Selection(
        selection=[
            ("included", "Included Products"),
            ("excluded", "Excluded Products"),
        ],
        string="Apply product filter",
        compute="_compute_apply_product_domain",
        store=True,
        readonly=False,
        help="Leave empty to ignore the fiscal position product domain. Select "
        "Included Products to apply this tax mapping line when the product matches "
        "the domain, or Excluded Products to apply it when the product does not "
        "match the domain.",
    )

    @api.depends("position_id")
    def _compute_apply_product_domain(self):
        for line in self:
            line.apply_product_domain = (
                "included"
                if line.position_id and line.position_id._has_product_domain()
                else False
            )

    def _is_applicable_to_product_template(self, template):
        self.ensure_one()
        product_domain = self.position_id.product_domain
        if not self.apply_product_domain:
            return True
        if not product_domain or product_domain == "[]":
            return True
        template_matches_domain = self.position_id._template_matches_product_domain(
            template, product_domain
        )
        if self.apply_product_domain == "excluded":
            return not template_matches_domain
        return template_matches_domain
