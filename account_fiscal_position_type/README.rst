.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Simplify taxes management for products
======================================

Functionality:
--------------
* Add a new light concept 'fiscal_classification' to associate possible
  purchase and sale taxes;

.. image:: https://raw.githubusercontent.com/akretion/account-fiscal-rule/8.0/account_product_fiscal_classification/static/description/img/fiscal_classification_form.png

* Make more usable taxes selection in product view. The user has now the
  possibility to select a fiscal classification, instead of select manually
  all the taxes;

.. image:: https://raw.githubusercontent.com/akretion/account-fiscal-rule/8.0/account_product_fiscal_classification/static/description/img/product_template_accounting_setting.png

* Prevent users to select incompatible purchase and sale taxes.
  French Exemple: A product can not be configured with:

  * Purchase Taxes: 5.5 %;
  * Sale Taxes: 20%;

* Provides the possibility to the account manager to change incorrect
  parameters massively;

Technical Information:
----------------------
* Install this module will create 'fiscal_classification' for each existing
  combination. Make sure that the user who install the module is
  SUPERUSER_ID or is member of account.group_account_manager;
* In the same way, import products will create fiscal_classification if
  combination doesn't exist and will fail if right access is not sufficient.
  A solution is to provide fiscal_classification_id during the import,
  instead of Providing taxes_id and purchase_taxes_id fields;

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-fiscal-rule/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-fiscal-rule/issues/new?body=module:%20account_product_fiscal_classification%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain);
* Sébastien BEAU <sebastien.beau@akretion.com>;
* Danimar RIBEIRO;

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

