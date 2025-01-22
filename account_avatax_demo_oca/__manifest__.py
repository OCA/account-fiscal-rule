{
    "name": "Avatax Demo",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": """
        This is a demo module for testing Avatax
    """,
    "website": "https://github.com/OCA/account-fiscal-rule",
    "author": "Kencove, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "website",
        "product",
        "queue_job",
        "account_avatax_oca",
        "account_avatax_sale_oca",
        "account_avatax_exemption_base",
        "account_avatax_exemption",
        "account_avatax_website_sale",
        "account_avatax_oca_log",
    ],
    "data": [
        "data/res_partner_exemption_business_type.xml",
    ],
    "external_dependencies": {"python": ["Avalara"]},
    "installable": True,
}
