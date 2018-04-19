import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-account-fiscal-rule",
    description="Meta package for oca-account-fiscal-rule Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-account_fiscal_position_rule',
        'odoo9-addon-account_fiscal_position_rule_purchase',
        'odoo9-addon-account_fiscal_position_rule_sale',
        'odoo9-addon-account_product_fiscal_classification',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
