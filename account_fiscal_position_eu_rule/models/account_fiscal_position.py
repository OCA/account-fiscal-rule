# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    def _get_fiscal_position(self, partner, delivery=None):
        """Resolve fiscal position using the seller + buyer + delivery triplet.

        Extends Odoo's native resolution with EU VAT rules.
        See readme/DESCRIPTION.rst for the full decision matrix.

        The ``seller`` and ``is_service`` parameters are read from the context
        (keys ``fp_eu_seller`` and ``fp_eu_is_service``) to avoid breaking the
        ``_get_fiscal_position()`` signature used by other modules (e.g.
        account_avatax_oca) that override the same method without knowing these
        parameters.

        Callers that want to pass a specific seller or flag a service
        transaction should use::

            env["account.fiscal.position"].with_context(
                fp_eu_seller=seller_partner,
                fp_eu_is_service=True,
            )._get_fiscal_position(partner, delivery=delivery)

        Re-entrancy guard
        -----------------
        When this module calls super(), the MRO may route the call back through
        our override (e.g. account_fiscal_position_partner_type calls its own
        super(), which lands here again).

        A universal guard ``fp_eu_in_progress`` is set at the very top of this
        method, before any logic or super() call.  On re-entry the flag is
        already True, so we skip all EU logic immediately and delegate to
        super() -- which continues down the remaining MRO layers
        (partner_type, Odoo stock) without ever re-entering this method.

        :param partner:    buyer/customer (res.partner)
        :param delivery:   delivery address (res.partner or None)
        :returns: account.fiscal.position record or empty recordset
        """
        eu_countries = self.env.ref("base.europe").country_ids
        if self.env.company.country_id not in eu_countries or self.env.context.get(
            "fp_eu_in_progress"
        ):
            return super()._get_fiscal_position(partner, delivery=delivery)

        self = self.with_context(fp_eu_in_progress=True)

        if partner.property_account_position_id:
            return partner.property_account_position_id

        seller = self.env.context.get("fp_eu_seller") or self.env.company.partner_id
        is_service = bool(self.env.context.get("fp_eu_is_service", False))

        seller_in_eu = seller.country_id in eu_countries
        buyer_in_eu = partner.country_id in eu_countries
        buyer_is_b2b = self._is_b2b_partner(partner)

        if not seller_in_eu:
            self = self.with_context(fiscal_position_type="b2b")
            return super()._get_fiscal_position(seller, delivery=None)

        # Art. 45: B2C services -> place of supply is always the seller's
        # country, regardless of where the buyer is located (EU or not).
        if is_service and not buyer_is_b2b:
            self = self.with_context(fiscal_position_type="b2b")
            return super()._get_fiscal_position(
                self._make_domestic_partner(seller), delivery=None
            )

        # Buyer outside EU: export for goods and B2B services (Art. 44).
        if not buyer_in_eu:
            return super()._get_fiscal_position(partner, delivery=None)

        if is_service:
            # Art. 44: B2B services -> place of supply is the buyer's country.
            self = self.with_context(fiscal_position_type="b2b")
            if partner.country_id == seller.country_id:
                return super()._get_fiscal_position(
                    self._make_domestic_partner(seller), delivery=None
                )
            return super()._get_fiscal_position(partner, delivery=None)

        delivery_country = (delivery or partner).country_id
        if delivery_country == seller.country_id:
            self = self.with_context(fiscal_position_type="b2b")
            return super()._get_fiscal_position(
                self._make_domestic_partner(seller), delivery=None
            )

        if not buyer_is_b2b:
            self = self.with_context(fiscal_position_type="b2c")
            return super()._get_fiscal_position(partner, delivery)
        self = self.with_context(fiscal_position_type="b2b")
        return super()._get_fiscal_position(partner, delivery=delivery)

    def _make_domestic_partner(self, seller):
        """Return a transient partner in the seller's country with a dummy VAT."""
        vals = {
            "country_id": seller.country_id.id,
            "vat": seller.country_id.code[:2] + "DOMESTIC",
        }
        if hasattr(self.env["res.partner"], "fiscal_position_type"):
            vals["fiscal_position_type"] = "b2b"
        return self.env["res.partner"].new(vals)

    def _is_b2b_partner(self, partner):
        """Return True if *partner* qualifies as a B2B taxable person.

        Priority order:
        1. vies_passed (OCA base_vat_optional_vies) -- only when VIES is
           activated on the company (vat_check_vies=True).
        2. fiscal_position_type (OCA account_fiscal_position_partner_type) --
           manually set by the user.
        3. Presence of a VAT number -- fallback.

        :param partner: res.partner record
        :returns: bool
        """
        if not partner.vat:
            return False
        if (
            hasattr(partner, "vies_passed")
            and hasattr(self.env.company, "vat_check_vies")
            and self.env.company.vat_check_vies
        ):
            return partner.vies_passed
        if hasattr(partner, "fiscal_position_type") and partner.fiscal_position_type:
            return partner.fiscal_position_type == "b2b"
        return True
