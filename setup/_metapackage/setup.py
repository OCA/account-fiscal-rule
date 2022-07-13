import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-account-fiscal-rule",
    description="Meta package for oca-account-fiscal-rule Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-account_fiscal_position_partner_type',
        'odoo12-addon-account_fiscal_position_type',
        'odoo12-addon-account_fiscal_position_usage_group',
        'odoo12-addon-account_product_fiscal_classification',
        'odoo12-addon-account_product_fiscal_classification_test',
        'odoo12-addon-l10n_eu_oss',
        'odoo12-addon-product_refund_account',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
