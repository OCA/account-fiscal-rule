# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from ast import literal_eval

from odoo import api, fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    partner_domain = fields.Char()

    def _get_base_domain(self, vat_required, company_id, partner_domain=False):
        base_domain = super()._get_base_domain(vat_required, company_id)
        extra_domain = (
            [("partner_domain", "!=", False), ("partner_domain", "!=", "[]")]
            if partner_domain
            else [("partner_domain", "=", False), ("partner_domain", "=", "[]")]
        )
        return base_domain + extra_domain

    @api.model
    def _get_fpos_by_region_with_domain(
        self,
        country_id=False,
        state_id=False,
        zipcode=False,
        vat_required=False,
        partner_id=False,
    ):
        if not country_id:
            return False
        company_id = self.env.context.get("force_company", self.env.company.id)
        base_domain = self._get_base_domain(vat_required, company_id, True)
        null_state_dom = state_domain = [("state_ids", "=", False)]
        null_zip_dom = zip_domain = [("zip_from", "=", False), ("zip_to", "=", False)]
        null_country_dom = [
            ("country_id", "=", False),
            ("country_group_id", "=", False),
        ]

        if zipcode:
            zip_domain = [("zip_from", "<=", zipcode), ("zip_to", ">=", zipcode)]

        if state_id:
            state_domain = [("state_ids", "=", state_id)]

        domain_country = base_domain + [("country_id", "=", country_id)]
        domain_group = base_domain + [("country_group_id.country_ids", "=", country_id)]

        # Build domain to search records with exact matching criteria
        fpos = self.search(domain_country + state_domain + zip_domain)
        # return records that fit the most the criteria, and fallback on less specific
        # fiscal positions if any can be found
        if not fpos and state_id:
            fpos = self.search(domain_country + null_state_dom + zip_domain)
        if not fpos and zipcode:
            fpos = self.search(domain_country + state_domain + null_zip_dom)
        if not fpos and state_id and zipcode:
            fpos = self.search(domain_country + null_state_dom + null_zip_dom)

        # fallback: country group with no state/zip range
        if not fpos:
            fpos = self.search(domain_group + null_state_dom + null_zip_dom)

        if not fpos:
            # Fallback on catchall (no country, no group)
            fpos = self.search(base_domain + null_country_dom)

        # Evaluate domain in the Fiscal Positions that have been found
        for fiscal_position in fpos:
            partner_domain = literal_eval(fiscal_position.partner_domain)
            partner = self.env["res.partner"].search(
                partner_domain + [("id", "=", partner_id)]
            )
            if partner:
                return fiscal_position

        return False

    @api.model
    def get_fiscal_position(self, partner_id, delivery_id=None):
        if not partner_id:
            return False
        # This can be easily overridden to apply more complex fiscal rules
        PartnerObj = self.env["res.partner"]
        partner = PartnerObj.browse(partner_id)

        # if no delivery use invoicing
        if delivery_id:
            delivery = PartnerObj.browse(delivery_id)
        else:
            delivery = partner

        # First search for Fiscal Positions the Odoo way
        fp = super().get_fiscal_position(partner_id, delivery_id)

        # partner manually set fiscal position always win
        if (
            delivery.property_account_position_id
            or partner.property_account_position_id
        ):
            return fp

        vat_required = bool(partner.vat)
        # Search for a Fiscal Position using the domain
        fp_partner_domain = self._get_fpos_by_region_with_domain(
            delivery.country_id.id,
            delivery.state_id.id,
            delivery.zip,
            vat_required,
            delivery.id,
        )
        if fp_partner_domain:
            return fp_partner_domain.id
        return fp
