# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    fiscal_position_type = fields.Selection(
        selection=[("b2c", "Customer"), ("b2b", "Company")],
        string="Type",
        default=lambda self: self._default_fiscal_position_type(),
    )

    @api.model
    def _default_fiscal_position_type(self):
        fiscal_position_type = None
        if self.env['res.company']._company_default_get():
            fiscal_position_type = self.env[
                'res.company']._company_default_get(
                    )[0].default_fiscal_position_type
        return fiscal_position_type

    @api.model
    def _get_fpos_by_region_and_position_type(
        self,
        country_id=False,
        state_id=False,
        zipcode=False,
        vat_required=False,
        position_type="b2c",
    ):
        if not country_id:
            return False
        company_id = self.env.context.get("force_company", self.env.company.id)
        base_domain = [
            ("auto_apply", "=", True),
            ("vat_required", "=", vat_required),
            ("company_id", "in", [company_id, False]),
            ("fiscal_position_type", "=", position_type),
        ]
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
        fpos = self.search(domain_country + state_domain + zip_domain, limit=1)
        # return records that fit the most the criteria, and fallback on
        # less specific fiscal positions if any can be found
        if not fpos and state_id:
            fpos = self.search(domain_country + null_state_dom + zip_domain, limit=1)
        if not fpos and zipcode:
            fpos = self.search(domain_country + state_domain + null_zip_dom, limit=1)
        if not fpos and state_id and zipcode:
            fpos = self.search(domain_country + null_state_dom + null_zip_dom, limit=1)

        # fallback: country group with no state/zip range
        if not fpos:
            fpos = self.search(domain_group + null_state_dom + null_zip_dom, limit=1)

        if not fpos:
            # Fallback on catchall (no country, no group)
            fpos = self.search(base_domain + null_country_dom, limit=1)
        return fpos or False

    @api.model
    def get_fiscal_position(self, partner_id, delivery_id=None):
        if not partner_id:
            return self.env["account.fiscal.position"]
        # This can be easily overridden to apply more complex fiscal rules
        PartnerObj = self.env["res.partner"]
        partner = PartnerObj.browse(partner_id)

        # if no delivery use invoicing
        if delivery_id:
            delivery = PartnerObj.browse(delivery_id)
        else:
            delivery = partner
        fp_id = self.env["account.fiscal.position"]
        # Only type has been configured
        if (
            delivery.commercial_partner_id.fiscal_position_type
            and not delivery.property_account_position_id
            and not delivery.commercial_partner_id.property_account_position_id
        ):
            # First search only matching VAT positions
            vat_required = bool(partner.vat)
            fp = self._get_fpos_by_region_and_position_type(
                delivery.country_id.id,
                delivery.state_id.id,
                delivery.zip,
                vat_required,
                delivery.commercial_partner_id.fiscal_position_type,
            )
            # Then if VAT required found no match, try positions that do not
            # require it
            if not fp and vat_required:
                fp = self._get_fpos_by_region_and_position_type(
                    delivery.country_id.id,
                    delivery.state_id.id,
                    delivery.zip,
                    False,
                    delivery.commercial_partner_id.fiscal_position_type,
                )
            if fp:
                fp_id = fp.id
        else:
            fp_id = super(AccountFiscalPosition, self).get_fiscal_position(
                partner_id, delivery_id
            )
        return fp_id
