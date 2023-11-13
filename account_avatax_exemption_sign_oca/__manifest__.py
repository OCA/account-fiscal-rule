# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2025 Kencove (https://www.kencove.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Avatax Exemptions with Sign OCA extension",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "summary": """
        This application allows you to add Avatax exemptions with Sign OCA module
    """,
    "website": "https://github.com/OCA/account-fiscal-rule",
    "author": "Kencove, ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "account_avatax_oca",
        "account_avatax_sale_oca",
        "account_avatax_exemption_base",
        "account_avatax_exemption",
        "sign_oca",
    ],
    "data": [
        "data/data.xml",
        "views/sign_oca_template.xml",
        "views/sign_oca_request.xml",
        "views/exemption_views.xml",
    ],
    "installable": True,
    "application": False,
}
