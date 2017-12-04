# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class AccountTaxTransactionLine(models.Model):

    _name = 'account.tax.transaction.line'
    _inherit = 'account.tax.rate.line'

    rate_id = fields.Many2one(
        string='Transaction',
        comodel_name='account.tax.transaction',
    )
