* Install this module will create 'fiscal_classification' for each existing
  combination. Make sure that the user who install the module is
  SUPERUSER_ID or is member of account.group_account_manager;
* In the same way, import products will create fiscal_classification if
  combination doesn't exist and will fail if right access is not sufficient.
  A solution is to provide fiscal_classification_id during the import,
  instead of Providing taxes_id and purchase_taxes_id fields;
