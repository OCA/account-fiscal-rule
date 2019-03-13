# Copyright (C) 2015 -Today Akretion (http://www.akretion.com)
#   @author Renato Lima (https://twitter.com/renatonlima)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountProductFiscalClassificationModel(models.AbstractModel):
    _name = 'account.product.fiscal.classification.model'
    _description = 'Fiscal Classification model'

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
