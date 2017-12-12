# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

# pylint: disable=C8101
{
    "name": "Sale Tax Connector",
    "summary": "Provides an adapter for sale order tax connectors.",
    "version": "10.0.1.0.0",
    "category": "Connector",
    "website": "https://laslabs.com",
    "author": "LasLabs",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "base_tax_connector",
        "sale",
    ],
}
