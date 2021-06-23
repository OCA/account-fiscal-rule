This module allows to define a partner domain in the Fiscal Position that will be used in the automatic
detection evaluation as follows:

* First, the system will look for a Fiscal Position using the Odoo standard approach
* Second, the system will try to look for a Fiscal Position applying the partner domain
* The system will return one of the found Fiscal Positions (if any) giving priority to the one that has a partner domain set
