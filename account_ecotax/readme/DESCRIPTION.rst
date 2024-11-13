This module adds ecotax amount on invoice line.
furthermore, a total ecotax is added at the footer of each document.

To make easy ecotaxe management and to factor the data, ecotaxes are set on products via ECOTAXE classifications.
ECOTAXE classification can either be a fixed or weight based ecotax.

A product can have one or serveral ecotax classifications. For example, wooden window blinds equipped with electric motor can
have ecotax for wood and ecotax for electric motor.

This module has some limits : 
- The ecotax amount is always included in the price of the product.
- The ecotax amount is not isolated in an specific accounting account but is included in the product income account.

If one of these limits is an issue, you could install the submodule account_ecotax_tax.
This second module lets you manage the ecotax as a tax, so you can configure if you want it to be included or excluded of product price and also configuring an accounting account to isolate it.
The main consequence of this approach is that the ecotax won't be considered in the turnover, since it is considered as a tax.

This module version add the possibility to manage several ecotax classifications by product.
A migration script is necessary to update from previous versions.

There is the main change to manage in migration script:

renamed field
model 			old field   		new field
account.move.line 	unit_ecotaxe_amount    ecotaxe_amount_unit
product.template        manual_fixed_ecotaxe   force_ecotaxe_amount

changed fields
model                 old field                    new field
product.template      ecotaxe_classification_id    ecotaxe_classification_ids

added fields
model 		    new field
account.move.line  ecotaxe_line_ids
product.template   ecotaxe_line_product_ids
