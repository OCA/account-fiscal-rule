import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-account-fiscal-rule",
    description="Meta package for oca-account-fiscal-rule Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_avatax_oca>=15.0dev,<15.1dev',
        'odoo-addon-account_avatax_sale_oca>=15.0dev,<15.1dev',
        'odoo-addon-account_fiscal_position_partner_type>=15.0dev,<15.1dev',
        'odoo-addon-l10n_eu_oss_oca>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
