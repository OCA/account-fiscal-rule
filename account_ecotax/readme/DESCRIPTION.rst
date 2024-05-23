This module applies to companies based in France mainland. It doesn't apply to
companies based in the DOM-TOMs (Guadeloupe, Martinique, Guyane, Réunion,
Mayotte).

It add Ecotaxe amount on invoice line.
furthermore, a total ecotaxe are added at the footer of each document.

To make easy ecotaxe management and to factor the data, ecotaxe are set on products via ECOTAXE classifications.
ECOTAXE classification can either a fixed or weight based ecotaxe.

A product can have one or serveral ecotaxe classifications. For exemple wooden window blinds equipped with electric motor can
have ecotaxe for wood and ecotaxe for electric motor.

This module version add the possibility to manage several ecotaxe classification by product.
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
