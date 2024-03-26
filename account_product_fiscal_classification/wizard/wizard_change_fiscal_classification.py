# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WizardChangeFiscalClassification(models.TransientModel):
    _name = "wizard.change.fiscal.classification"
    _description = "Wizard : Change fiscal classification on product"

    # Getter / Setter Section
    def _default_old_fiscal_classification_id(self):
        return self.env.context.get("active_id", False)

    # Field Section
    old_fiscal_classification_id = fields.Many2one(
        comodel_name="account.product.fiscal.classification",
        string="Old Classification",
        default=_default_old_fiscal_classification_id,
        readonly=True,
    )

    new_fiscal_classification_id = fields.Many2one(
        comodel_name="account.product.fiscal.classification",
        string="New Classification",
        required=True,
        domain="[('id', '!=', old_fiscal_classification_id)]",
    )

    # View Section
    def button_change_fiscal_classification(self):
        self.ensure_one()
        self.old_fiscal_classification_id.product_tmpl_ids.write(
            {"fiscal_classification_id": self.new_fiscal_classification_id.id}
        )
