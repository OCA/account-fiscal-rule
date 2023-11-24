import logging

from odoo import _, api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    @api.constrains("country_id", "foreign_vat")
    def _validate_foreign_vat(self):
        for record in self:
            try:
                super()._validate_foreign_vat()
            except Exception as e:
                checked_country_code = self.env["res.partner"]._run_vat_test(
                    record.foreign_vat, record.country_id
                )

                if (
                    checked_country_code
                    and record.country_id
                    and checked_country_code != record.country_id.code.lower()
                ):
                    raise ValidationError(
                        _(
                            "The country detected for this foreign VAT "
                            "number does not match the one set on this fiscal position."
                        )
                    ) from e
                if not checked_country_code and not record.country_id:
                    raise ValidationError(
                        _("The foreign VAT number is not correct.")
                    ) from e
                if not checked_country_code:
                    fp_label = _("fiscal position [%s]", record.name)
                    error_message = self.env["res.partner"]._build_vat_error_message(
                        record.country_id.code.lower(), record.foreign_vat, fp_label
                    )
                    raise ValidationError(error_message) from e
        return True

    @api.constrains("country_id", "state_ids", "foreign_vat")
    def _validate_foreign_vat_country(self):
        for _record in self:
            try:
                super()._validate_foreign_vat_country()
            except ValidationError:
                _logger.info("Ignored foreign vat country constrains")
            except Exception as e:
                raise e
        return True
