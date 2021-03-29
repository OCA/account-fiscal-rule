import logging

from odoo import _, http
from odoo.http import request, route
from odoo.tools import exception_to_unicode

from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class Exemption(http.Controller):
    @http.route("/exemption/<int:exemption_id>", website=True, auth="public")
    def get_exemption(self, **kw):
        exemption_id = kw.get("exemption_id")
        try:
            message = (
                request.env["res.partner.exemption"]
                .sudo()
                .search_exemption_line(exemption_id)
            )
        except Exception as e:
            message = False, exception_to_unicode(e)
        return request.render(
            "account_avatax_exemption.exemption_page", {"message": message}
        )


class WebsiteExemption(CustomerPortal):
    def _exemptions_domain(self, search=""):
        """Get user's exemptions domain."""

        avalara_salestax = (
            request.env["avalara.salestax"]
            .sudo()
            .search([("exemption_export", "=", True)], limit=1)
        )
        domain = [("partner_id", "child_of", request.env.user.partner_id.id)]
        if avalara_salestax.use_commercial_entity:
            domain = [
                (
                    "partner_id",
                    "child_of",
                    request.env.user.partner_id.commercial_partner_id.id,
                )
            ]

        return domain

    def _prepare_portal_layout_values(self, exemption=None):
        values = super(WebsiteExemption, self)._prepare_portal_layout_values()
        partner_counts = request.env["res.partner.exemption"].search_count(
            self._exemptions_domain()
        )
        values["exemption_count"] = partner_counts
        return values

    def _prepare_exemptions_values(
        self, page=1, date_begin=None, date_end=None, search="", sortby=None
    ):
        """Prepare the rendering context for the exemptions list."""
        values = self._prepare_portal_layout_values()
        Exemption = request.env["res.partner.exemption"]
        base_url = "/my/exemptions"

        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "expiry_date": {"label": _("Expiry Date"), "order": "expiry_date desc"},
        }
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        # Get the required domains
        domain = self._exemptions_domain(search)

        if date_begin and date_end:
            domain += [
                ("create_date", ">=", date_begin),
                ("create_date", "<", date_end),
            ]

        # Make pager
        pager = request.website.pager(
            url=base_url,
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=Exemption.search_count(domain),
            page=page,
            step=self._items_per_page,
        )

        # Current records to display
        exemptions = Exemption.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager["offset"],
        )
        request.session["my_exemptions_history"] = exemptions.ids[:100]

        values.update(
            {
                "date": date_begin,
                "date_end": date_end,
                "exemptions": exemptions,
                "page_name": "exemption",
                "pager": pager,
                "default_url": base_url,
                "search": search,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )

        return values

    def _exemptions_fields(self):
        """Fields to display in the form."""
        return [
            "partner_id",
            "exemption_type",
            "exemption_code_id",
            "state",
            "exemption_number",
            "exemption_number_type",
            "effective_date",
            "expiry_date",
        ]

    @route(
        ["/my/exemptions", "/my/exemptions/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_exemptions(
        self, page=1, date_begin=None, date_end=None, sortby=None, search="", **kw
    ):
        """List all of your exemptions."""
        values = self._prepare_exemptions_values(
            page, date_begin, date_end, search, sortby
        )
        return request.render("account_avatax_exemption.portal_my_exemptions", values)

    def _exemption_get_page_view_values(self, exemption, access_token, **kwargs):
        values = {
            "exemption": exemption,
            "fields": self._exemptions_fields(),
            "page_name": "exemption",
            "user": request.env.user,
        }

        return self._get_page_view_values(
            exemption, access_token, values, "my_exemption_history", False, **kwargs
        )

    @route(
        ["/my/exemptions/<model('res.partner.exemption'):exemption>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_exemptions_read(self, exemption, access_token=None, **kw):
        """Read a exemption form."""
        values = self._exemption_get_page_view_values(exemption, access_token, **kw)
        return request.render("account_avatax_exemption.exemptions_followup", values)
