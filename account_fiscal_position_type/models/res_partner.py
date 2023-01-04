# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains(
        'customer', 'supplier', 'property_account_position_id', 'parent_id')
    def _check_fiscal_position_type(self):
        # only apply constraint on parent partner
        # Child partners inherit from the configuration
        # of the parent, whatever their configuration
        for partner in self.filtered(
            lambda x: x.property_account_position_id and not x.parent_id
        ):
            position = partner.property_account_position_id
            if not partner.customer and\
                    position.type_position_use == 'sale':
                raise ValidationError(_(
                    "You have selected a Sale fiscal position for a non"
                    " customer partner."))
            if not partner.supplier and\
                    position.type_position_use == 'purchase':
                raise ValidationError(_(
                    "You have selected a Purchase fiscal position for a non"
                    " supplier partner."))
