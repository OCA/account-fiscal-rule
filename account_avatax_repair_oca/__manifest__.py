{
    "name": "Avalara Avatax Certified Connector for Repair Orders",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "summary": "Repair Orders with automatic Tax application using Avatax",
    "license": "AGPL-3",
    "category": "Inventory",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "depends": ["account_avatax_oca", "repair"],
    "data": [
        "views/repair_order_view.xml",
        "views/avalara_salestax_view.xml",
        "views/partner_view.xml",
    ],
    "auto_install": True,
}
