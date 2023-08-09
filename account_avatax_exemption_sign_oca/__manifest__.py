# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Avatax Exemptions with Sign OCA extension",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "summary": """
        This application allows you to add Avatax exemptions with Sign OCA module
    """,
    "website": "https://github.com/OCA/sign",
    "author": "ForgeFlow",
    "license": "AGPL-3",
    "depends": [
        "account_avatax_oca",
        "account_avatax_sale_oca",
        "account_avatax_exemption",
        "sign_oca",
    ],
    "data": [
        "data/data.xml",
        "views/sign_oca_template.xml",
        "views/sign_oca_request.xml",
    ],
    "installable": True,
    "application": False,
}
