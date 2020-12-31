{
    "name": "Avatax Exemptions Base",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "summary": """
        This application allows you to add exemptions base to Avatax
    """,
    "website": "https://github.com/OCA/account-fiscal-rule",
    "author": "Sodexis, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": [
        "account_avatax",
        "account_avatax_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/res_country_state_view.xml",
        "views/partner_view.xml",
        "views/avalara_exemption_view.xml",
    ],
    "installable": True,
    "application": False,
}
