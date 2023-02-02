This module extends the functionality of account to add a use type on
fiscal position. (``sale``, ``purchase`` or ``all``) to restrict the
usage of fiscal position for out or in invoices.

* If a fiscal position is configured for sale, it will not be possible to use it
  on Vendor Bills, Refunds and Purchase Receipts.

* If a fiscal position is configured for purchase, it will not be possible to use it
  on Customer Invoices, Credit Notes and Sales Receipts.
