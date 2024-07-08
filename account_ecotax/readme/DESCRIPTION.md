This module applies to companies based in France mainland. It doesn't
apply to companies based in the DOM-TOMs (Guadeloupe, Martinique,
Guyane, Réunion, Mayotte).

It add Ecotax amount on invoice line. furthermore, a total ecotax are
added at the footer of each document.

To make easy ecotax management and to factor the data, ecotax are set
on products via ECOTAXE classifications. ECOTAXE classification can
either a fixed or weight based ecotax.

A product can have one or serveral ecotax classifications. For exemple
wooden window blinds equipped with electric motor can have ecotax for
wood and ecotax for electric motor.

This module version add the possibility to manage several ecotax
classification by product. A migration script is necessary to update
from previous versions.

There is the main change to manage in migration script:

renamed field model old field new field account.move.line
unit_ecotax_amount ecotax_amount_unit product.template
manual_fixed_ecotax force_ecotax_amount

changed fields model old field new field product.template
ecotax_classification_id ecotax_classification_ids

added fields model new field account.move.line ecotax_line_ids
product.template ecotax_line_product_ids
