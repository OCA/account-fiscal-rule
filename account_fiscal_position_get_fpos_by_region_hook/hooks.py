# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.account.models.partner import AccountFiscalPosition


def post_load_hook():
    def _get_fpos_by_region_new(
        self, country_id=False, state_id=False, zipcode=False, vat_required=False
    ):

        if not hasattr(self, "_get_base_domain"):
            return self._get_fpos_by_region(country_id, state_id, zipcode, vat_required)

        if not country_id:
            return False
        company_id = self.env.context.get("force_company", self.env.company.id)
        # START OF THE HOOK
        base_domain = self._get_base_domain(vat_required, company_id)
        # END OF THE HOOK
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
        # return records that fit the most the criteria, and fallback on less specific
        # fiscal positions if any can be found
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

    if not hasattr(AccountFiscalPosition, "_get_fpos_by_region_original"):
        AccountFiscalPosition._get_fpos_by_region_original = (
            AccountFiscalPosition._get_fpos_by_region
        )

    AccountFiscalPosition._get_fpos_by_region = _get_fpos_by_region_new
