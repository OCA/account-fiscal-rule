# Copyright (C) 2019-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    classification_template_ids = fields.One2many(
        comodel_name="account.product.fiscal.classification.template",
        inverse_name="chart_template_id",
        string="Fiscal Classification Templates",
    )

    def _load_template(
        self, company, code_digits=None, account_ref=None, taxes_ref=None
    ):
        self.ensure_one()
        AccountProductFiscalClassification = self.env[
            "account.product.fiscal.classification"
        ]

        res = super()._load_template(
            company,
            code_digits=code_digits,
            account_ref=account_ref,
            taxes_ref=taxes_ref,
        )

        # Create classification, based on classification template
        taxes_ref = res[1]

        for template in self.classification_template_ids:
            vals = template._prepare_fiscal_classification(company, taxes_ref)
            AccountProductFiscalClassification.create(vals)
        return res
