This module extends the functionality of account to add a use type on
fiscal position. (``sale``, ``purchase`` or ``all``) to restrict the
usage of fiscal position for out or in invoices.

* If a fiscal position is configured for sale, it will not be possible to use
  it in a purchase invoice.

* If a fiscal position is configured for sale, it will not be possible to
  set it to a partner flagged only as 'supplier'
