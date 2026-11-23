# Copyright 2024 Akretion (https://www.akretion.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ecotax_tax_ids = fields.One2many(
        "account.tax",
        "company_id",
        string="Ecotax Taxes",
        domain=[("is_ecotax", "=", True)],
        help="Ecotax taxes defined for this company.",
    )

    def action_create_ecotax_tax(self):
        """Create a default ecotax tax for this company from the template.

        Copies the template ``tax_ecotax`` (company_id=1) with the correct
        ``company_id`` and a matching tax group.  If an ecotax tax already
        exists for the company, it is returned instead of creating a
        duplicate.
        """
        self.ensure_one()
        existing = self.env["account.tax"].search(
            [("is_ecotax", "=", True), ("company_id", "=", self.id)], limit=1
        )
        if existing:
            return existing
        template = self.env.ref(
            "account_ecotax_tax.tax_ecotax", raise_if_not_found=False
        )
        if not template:
            return self.env["account.tax"]
        # sudo: template belongs to company 1; we bypass multi-company rules
        # to read and copy it, then assign the new tax to self.id.
        template = template.sudo()
        defaults = {
            "company_id": self.id,
            "country_id": self.country_id.id or template.country_id.id,
            "name": template.name,
        }
        tax_group = template.tax_group_id
        if tax_group and tax_group.company_id and tax_group.company_id != self:
            tax_group = self._get_or_create_ecotax_tax_group(tax_group)
            defaults["tax_group_id"] = tax_group.id
        return template.copy(defaults)

    def _get_or_create_ecotax_tax_group(self, tax_group):
        """Return a tax group for this company, copying ``tax_group`` if needed."""
        self.ensure_one()
        existing = self.env["account.tax.group"].search(
            [
                ("company_id", "=", self.id),
                ("country_id", "=", tax_group.country_id.id),
                ("name", "=", tax_group.name),
            ],
            limit=1,
        )
        if existing:
            return existing
        return tax_group.sudo().copy(
            {
                "company_id": self.id,
                "country_id": self.country_id.id or tax_group.country_id.id,
            }
        )
