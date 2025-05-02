import logging

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class RetailDeliveryFee(models.Model):
    _name = "avatax.retail.delivery.fee"
    _description = "Retail Delivery Fee (RDF)"

    country_id = fields.Many2one(
        "res.country",
        required=True,
    )
    state_id = fields.Many2one(
        "res.country.state",
        required=True,
    )
    amount = fields.Float()
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
    )
    tax_ids = fields.Many2many(
        "account.tax",
        string="Taxes",
        domain=[("amount_type", "=", "fixed")],
        required=True,
    )
    enabled = fields.Boolean(default=True, help="Enable This RDF")
    condition_expression = fields.Text(
        help="Python expression that returns True to apply RDF. "
        "Example: order.amount_total >= 100",
    )

    def name_get(self):
        res = []
        for record in self:
            name = "{} ({}) - {}".format(
                record.state_id.name or "", record.country_id.name or "", record.amount
            )
            res.append((record.id, name))
        return res

    def should_apply_to(self, order):
        """Determine whether to apply RDF to the given order."""
        self.ensure_one()
        if not self.enabled:
            return False
        if self.condition_expression and self.condition_expression.strip():
            localdict = {"order": order}
            try:
                result = bool(safe_eval(self.condition_expression.strip(), localdict))
                _logger.debug(
                    "Evaluated RDF condition for order %s: %s = %s",
                    order.id,
                    self.condition_expression,
                    result,
                )
                return result
            except Exception as e:
                _logger.warning("Invalid RDF condition: %s", str(e))
                return False
        return True
