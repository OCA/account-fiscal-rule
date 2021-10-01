# -*- encoding: utf-8 -*-
# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    oss_country_id = fields.Many2one(comodel_name="res.country", string="Oss Country",)


class AccountTaxCode(models.Model):
    _inherit = "account.tax.code"

    oss_country_id = fields.Many2one(comodel_name="res.country", string="Oss Country",)
