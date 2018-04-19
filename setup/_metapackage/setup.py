import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-account-fiscal-rule",
    description="Meta package for oca-account-fiscal-rule Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-account_fiscal_position_rule',
        'odoo8-addon-account_fiscal_position_rule_purchase',
        'odoo8-addon-account_fiscal_position_rule_sale',
        'odoo8-addon-account_fiscal_position_rule_stock',
        'odoo8-addon-account_product_fiscal_classification',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
