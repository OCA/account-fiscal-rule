import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-account-fiscal-rule",
    description="Meta package for oca-account-fiscal-rule Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-account_fiscal_position_rule',
        'odoo10-addon-account_fiscal_position_rule_purchase',
        'odoo10-addon-account_fiscal_position_rule_sale',
        'odoo10-addon-account_fiscal_position_rule_sale_stock',
        'odoo10-addon-account_fiscal_position_rule_stock',
        'odoo10-addon-account_product_fiscal_classification',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
