import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-account-fiscal-rule",
    description="Meta package for oca-account-fiscal-rule Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_avatax',
        'odoo14-addon-account_avatax_exemption',
        'odoo14-addon-account_avatax_exemption_base',
        'odoo14-addon-account_avatax_sale',
        'odoo14-addon-account_avatax_website_sale',
        'odoo14-addon-account_fiscal_position_partner_type',
        'odoo14-addon-account_product_fiscal_classification',
        'odoo14-addon-account_product_fiscal_classification_test',
        'odoo14-addon-l10n_eu_oss',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
