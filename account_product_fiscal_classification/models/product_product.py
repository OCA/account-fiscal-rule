# Copyright (C) 2025-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from lxml import etree

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Set fiscal_classification_id required on all views.
        We don't set the field required by field definition to avoid
        incompatibility with other modules, errors on import, etc..."""
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        doc = etree.fromstring(result["arch"])
        nodes = doc.xpath("//field[@name='fiscal_classification_id']")
        if nodes:
            for node in nodes:
                modifiers = json.loads(node.get("modifiers", "{}"))
                modifiers["required"] = True
                node.set("modifiers", json.dumps(modifiers))
            result["arch"] = etree.tostring(doc, encoding="unicode").replace("\t", "")
        return result
