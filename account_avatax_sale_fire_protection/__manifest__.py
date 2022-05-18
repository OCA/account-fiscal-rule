{
    "name": "Florida Taxation for Labor Products",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Accounting",
    "summary": """For Delivery Address in state of Florida,
    applies conditional replacement on Sale Order
    products of non-taxable labor products.""",
    "author": "Odoo Community Association (OCA),Open Source Integrators",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "depends": ["account_avatax_sale"],
    "data": ["views/product_view.xml", "views/sale_order_view.xml"],
    "installable": True,
}
