{
    "name": "Account Avatax OCA Log",
    "version": "16.0.1.0.0",
    "author": "Open Source Integrators, ForgeFlow, Odoo Community Association (OCA)",
    "summary": "Add Logs to Avatax calls",
    "license": "AGPL-3",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "depends": ["account_avatax_oca"],
    "data": [
        "security/ir.model.access.csv",
        "data/cron.xml",
        "data/emails.xml",
        "views/res_config_settings_views.xml",
        "views/avatax_log_views.xml",
    ],
    "auto_install": False,
    "development_status": "Alpha",
}
