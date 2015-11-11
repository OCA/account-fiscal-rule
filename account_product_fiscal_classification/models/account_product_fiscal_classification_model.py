# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Product - Fiscal Classification module for Odoo
#    Copyright (C) 2015 -Today Akretion (http://www.akretion.com)
#    @author Renato Lima (https://twitter.com/renatonlima)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import models, fields


class AccountProductFiscalClassificationModel(models.AbstractModel):
    """Fiscal Classification model of customer and supplier taxes.
    This classification is used to create Fiscal Classification
    and Fiscal Classification template."""
    _name = 'account.product.fiscal.classification.model'
    _MAX_LENGTH_NAME = 256

    # Field Section
    code = fields.Char()

    name = fields.Char(
        size=_MAX_LENGTH_NAME, required=True, select=True, translate=True)

    description = fields.Text()

    active = fields.Boolean(
        default=True,
        help="If unchecked, it will allow you to hide the Fiscal"
        " Classification without removing it.")
