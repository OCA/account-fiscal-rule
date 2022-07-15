{
    "name": "Avalara Avatax Connector for Sales Orders",
    "version": "13.0.2.4.3",
    "author": "Fabrice Henrion, Odoo Community Association (OCA)",
    "summary": "Sales Orders with automatic Tax application using Avatax",
    "license": "AGPL-3",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "depends": ["account_avatax", "sale"],
    "data": ["views/sale_order_view.xml", "views/partner_view.xml"],
    "auto_install": True,
    "development_status": "Beta",
    "maintainers": ["dreispt"],
}
