import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-account-fiscal-rule",
    description="Meta package for oca-account-fiscal-rule Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_avatax_exemption_base>=16.0dev,<16.1dev',
        'odoo-addon-account_avatax_oca>=16.0dev,<16.1dev',
        'odoo-addon-account_avatax_sale_oca>=16.0dev,<16.1dev',
        'odoo-addon-account_avatax_website_sale>=16.0dev,<16.1dev',
        'odoo-addon-account_fiscal_position_autodetect_optional_vies>=16.0dev,<16.1dev',
        'odoo-addon-account_fiscal_position_partner_type>=16.0dev,<16.1dev',
        'odoo-addon-account_fiscal_position_type>=16.0dev,<16.1dev',
        'odoo-addon-account_product_fiscal_classification>=16.0dev,<16.1dev',
        'odoo-addon-l10n_eu_oss_oca>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
