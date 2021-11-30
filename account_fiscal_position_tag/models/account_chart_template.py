# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _get_fp_vals(self, company, position):
        res = super()._get_fp_vals(company, position)
        res.update(
            {
                "tag_ids": [(6, 0, position.tag_ids.ids)],
            }
        )
        return res
