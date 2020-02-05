When printing the invoice report, the company VAT number will be seeked in the following way:

#. **If there is a fiscal position which has a tax administration:** try to find a VAT number
   matching the tax administration.
#. **If there is no fiscal position on the invoice or no tax administration on
   the fiscal position:** try to find a VAT number matching the country of the company.
#. **If nothing found:** the standard VAT number on the company is used.

and the customer VAT number:
#. **If there is a delivery address:** try to find a tax administration matching the country of the address.
#. **If there is no delivery address on the invoice or no tax administration found or no VAT number found:** the standard VAT number on the customer is used.
