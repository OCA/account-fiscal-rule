{
    "name": "Avatax Exemptions Base",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": """
        This application allows you to add exemptions base to Avatax
    """,
    "website": "https://github.com/OCA/account-fiscal-rule",
    "author": "Sodexis, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": [
        "mail",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/res_country_state_view.xml",
        "views/avalara_exemption_view.xml",
    ],
    "images": ["static/description/avatax_icon.png"],
    "installable": True,
    "application": False,
}
