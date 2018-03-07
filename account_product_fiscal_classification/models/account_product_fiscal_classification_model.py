# -*- coding: utf-8 -*-
# Copyright (C) 2015 -Today Akretion (http://www.akretion.com)
#   @author Renato Lima (https://twitter.com/renatonlima)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountProductFiscalClassificationModel(models.AbstractModel):
    """Fiscal Classification model of customer and supplier taxes.
    This classification is used to create Fiscal Classification
    and Fiscal Classification template."""
    _name = 'account.product.fiscal.classification.model'
    _MAX_LENGTH_NAME = 256

    # Field Section
    code = fields.Char()

    name = fields.Char(
        size=_MAX_LENGTH_NAME, required=True, index=True, translate=True)

    description = fields.Text()

    active = fields.Boolean(
        default=True,
        help="If unchecked, it will allow you to hide the Fiscal"
        " Classification without removing it.")
