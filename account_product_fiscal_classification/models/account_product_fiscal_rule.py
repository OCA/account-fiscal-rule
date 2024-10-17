# Copyright (C) 2022-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountProductFiscalRule(models.Model):
    _name = "account.product.fiscal.rule"
    _description = "Fiscal Rule"
    _order = "sequence, company_id"

    sequence = fields.Integer(default=10)

    category_ids = fields.Many2many(comodel_name="product.category")

    fiscal_classification_ids = fields.Many2many(
        comodel_name="account.product.fiscal.classification",
        relation="fiscal_rule_fiscal_classification_rel",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda x: x._default_company_id(),
        string="Company",
    )

    action = fields.Selection(
        selection=[("forbid", "Forbid"), ("allow", "Allow")],
        required=True,
        default="forbid",
    )

    message = fields.Text()

    def _default_company_id(self):
        return self.env.company

    @api.model
    def check_product_templates_integrity(self, templates):
        # We assume that accountants know set correctly fiscal settings
        # and can bypass rules
        if self.env.user.has_group("account.group_account_manager"):
            return True

        for template in templates:
            # Get rules that matches the template
            categ_domain = [
                "|",
                ("category_ids", "=", template.categ_id.id),
                ("category_ids", "=", False),
            ]
            fiscal_domain = [
                "|",
                (
                    "fiscal_classification_ids",
                    "=",
                    template.fiscal_classification_id.id,
                ),
                ("fiscal_classification_ids", "=", False),
            ]
            rules = self.search(categ_domain + fiscal_domain)
            for rule in rules:
                # If an explicit rule allow that configuration, exit
                if rule.action == "allow":
                    break
                elif rule.action == "forbid":
                    raise ValidationError(
                        _(
                            "Incorrect Fiscal Setting :\n"
                            "- Category : %(categ_name)s\n"
                            "- Fiscal Classification : %(fiscal_name)s\n\n"
                            "%(extra_message)s",
                            categ_name=template.categ_id.complete_name,
                            fiscal_name=template.fiscal_classification_id.name,
                            extra_message=rule.message or "",
                        )
                    )
        return True
