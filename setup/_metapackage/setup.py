import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-account-fiscal-rule",
    description="Meta package for oca-account-fiscal-rule Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-account_fiscal_position_partner_type',
        'odoo11-addon-l10n_eu_oss',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
