from unittest import mock

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.account_avatax_oca.models.avatax_rest_api import AvaTaxRESTService


@tagged("post_install", "-at_install")
class TestRepair(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        # AvaTaxRESTService
        cls.avatax = cls.env["avalara.salestax"].create(
            {
                "account_number": "1234",
                "license_key": "1234",
                "service_url": "https://rest.avatax.com/api/v2",
                "company_code": "PA2",
                "logging": True,
                "use_so_partner_id": True,
                "invoice_calculate_tax": True,
                "repair_calculate_tax": True,
                "disable_tax_calculation": False,
                "company_id": cls.env.company.id,
            }
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "AVATAX-TEST",
                "amount_type": "percent",
                "type_tax_use": "sale",
                "is_avatax": True,
                "tax_group_id": cls.env.ref("account.tax_group_taxes").id,
                "company_id": cls.env.company.id,
            }
        )
        fpos = cls.env["account.fiscal.position"].create(
            {
                "name": "FPOS Avatax",
                "is_avatax": True,
                "company_id": cls.env.company.id,
            }
        )

        # Partners
        cls.res_partner = cls.env["res.partner"].create(
            {
                "name": "Repair customer",
                "property_account_position_id": fpos.id,
                "street": "street",
                "zip": "1234",
                "city": "bcn",
                "country_id": cls.env.ref("base.us").id,
                "property_exemption_number": "111",
                "property_tax_exempt": True,
            }
        )

        # Products
        cls.product_product_3 = cls.env["product.product"].create(
            {"name": "Desk Combination"}
        )
        cls.product_product_11 = cls.env["product.product"].create(
            {"name": "Conference Chair"}
        )
        cls.product_product_5 = cls.env["product.product"].create({"name": "Product 5"})
        cls.product_product_6 = cls.env["product.product"].create(
            {"name": "Large Cabinet"}
        )
        cls.product_product_12 = cls.env["product.product"].create(
            {"name": "Office Chair Black"}
        )
        cls.product_product_13 = cls.env["product.product"].create(
            {"name": "Corner Desk Left Sit"}
        )
        cls.product_product_2 = cls.env["product.product"].create(
            {"name": "Virtual Home Staging"}
        )
        cls.product_service_order_repair = cls.env["product.product"].create(
            {
                "name": "Repair Services",
                "type": "service",
            }
        )
        cls.env.company.partner_id.street = "street"

        # Location
        cls.stock_warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location_14 = cls.env["stock.location"].create(
            {
                "name": "Shelf 2",
                "location_id": cls.stock_warehouse.lot_stock_id.id,
            }
        )

    def test_00_repair(self):
        product_to_repair = self.product_product_5
        product_to_add = self.product_product_5
        partner = self.res_partner
        mock_api_call = mock.patch.object(AvaTaxRESTService, "get_tax")
        with mock_api_call as mock_func:
            mock_func.return_value = {
                "id": 0,
                "code": "invented code",
                "companyId": 123456,
                "date": "2023-07-21",
                "paymentDate": "2023-07-21",
                "status": "Temporary",
                "type": "SalesOrder",
                "batchCode": "",
                "currencyCode": "USD",
                "exchangeRateCurrencyCode": "USD",
                "customerUsageType": "",
                "entityUseCode": "",
                "customerVendorCode": "1689678087-0-Cust-43",
                "customerCode": "1689678087-0-Cust-43",
                "exemptNo": "",
                "reconciled": False,
                "locationCode": "",
                "reportingLocationCode": "",
                "purchaseOrderNo": "",
                "referenceCode": "",
                "salespersonCode": "Mitchell Admin",
                "totalAmount": 320.0,
                "totalExempt": 0.0,
                "totalDiscount": 0.0,
                "totalTax": 19.52,
                "totalTaxable": 320.0,
                "totalTaxCalculated": 19.52,
                "adjustmentReason": "NotAdjusted",
                "locked": False,
                "version": 1,
                "exchangeRateEffectiveDate": "2023-07-21",
                "exchangeRate": 1.0,
                "description": "RMA/00070",
                "modifiedDate": "2023-07-21T15:02:45.2078018Z",
                "modifiedUserId": 1094294,
                "taxDate": "2023-07-21",
                "lines": [
                    {
                        "id": 0,
                        "transactionId": 0,
                        "lineNumber": "999",
                        "customerUsageType": "",
                        "entityUseCode": "",
                        "description": "[E-COM07] Large Cabinet",
                        "discountAmount": 0.0,
                        "exemptAmount": 0.0,
                        "exemptCertId": 0,
                        "exemptNo": "",
                        "isItemTaxable": True,
                        "itemCode": "E-COM07",
                        "lineAmount": 320.0,
                        "quantity": 1.0,
                        "ref1": "",
                        "ref2": "",
                        "reportingDate": "2023-07-21",
                        "tax": 19.52,
                        "taxableAmount": 320.0,
                        "taxCalculated": 19.52,
                        "taxCode": "P0000000",
                        "taxCodeId": 4316,
                        "taxDate": "2023-07-21",
                        "taxIncluded": False,
                        "details": [
                            {
                                "id": 0,
                                "transactionLineId": 0,
                                "transactionId": 0,
                                "country": "US",
                                "region": "AZ",
                                "exemptAmount": 0.0,
                                "jurisCode": "04",
                                "jurisName": "ARIZONA",
                                "stateAssignedNo": "",
                                "jurisType": "STA",
                                "jurisdictionType": "State",
                                "nonTaxableAmount": 0.0,
                                "rate": 0.056,
                                "tax": 17.92,
                                "taxableAmount": 320.0,
                                "taxType": "Sales",
                                "taxSubTypeId": "S",
                                "taxName": "AZ STATE TAX",
                                "taxAuthorityTypeId": 45,
                                "taxCalculated": 17.92,
                                "rateType": "General",
                                "rateTypeCode": "G",
                                "unitOfBasis": "PerCurrencyUnit",
                                "isNonPassThru": False,
                                "isFee": False,
                                "reportingTaxableUnits": 320.0,
                                "reportingNonTaxableUnits": 0.0,
                                "reportingExemptUnits": 0.0,
                                "reportingTax": 17.92,
                                "reportingTaxCalculated": 17.92,
                                "liabilityType": "Seller",
                                "chargedTo": "Buyer",
                            },
                            {
                                "id": 0,
                                "transactionLineId": 0,
                                "transactionId": 0,
                                "country": "US",
                                "region": "AZ",
                                "exemptAmount": 0.0,
                                "jurisCode": "019",
                                "jurisName": "PIMA",
                                "stateAssignedNo": "PMA",
                                "jurisType": "CTY",
                                "jurisdictionType": "County",
                                "nonTaxableAmount": 0.0,
                                "rate": 0.005,
                                "tax": 1.6,
                                "taxableAmount": 320.0,
                                "taxType": "Sales",
                                "taxSubTypeId": "S",
                                "taxName": "AZ COUNTY TAX",
                                "taxAuthorityTypeId": 45,
                                "taxCalculated": 1.6,
                                "rateType": "General",
                                "rateTypeCode": "G",
                                "unitOfBasis": "PerCurrencyUnit",
                                "isNonPassThru": False,
                                "isFee": False,
                                "reportingTaxableUnits": 320.0,
                                "reportingNonTaxableUnits": 0.0,
                                "reportingExemptUnits": 0.0,
                                "reportingTax": 1.6,
                                "reportingTaxCalculated": 1.6,
                                "liabilityType": "Seller",
                                "chargedTo": "Buyer",
                            },
                        ],
                        "nonPassthroughDetails": [],
                        "hsCode": "",
                        "costInsuranceFreight": 0.0,
                        "vatCode": "",
                        "vatNumberTypeId": 0,
                        "rate": 6.1,
                    }
                ],
                "addresses": [
                    {
                        "id": 0,
                        "transactionId": 0,
                        "boundaryLevel": "Address",
                        "line1": "13035 N TEAL BLUE TRL",
                        "line2": "",
                        "line3": "",
                        "city": "TUCSON",
                        "region": "AZ",
                        "postalCode": "85742-8879",
                        "country": "US",
                        "taxRegionId": 1234,
                        "latitude": "32.442129",
                        "longitude": "-111.033853",
                    },
                    {
                        "id": 0,
                        "transactionId": 0,
                        "boundaryLevel": "Address",
                        "line1": "250 Executive Park Blvd, Suite 3400",
                        "line2": "",
                        "line3": "",
                        "city": "San Francisco",
                        "region": "CA",
                        "postalCode": "94134",
                        "country": "US",
                        "taxRegionId": 1234,
                        "latitude": "37.71116",
                        "longitude": "-122.391717",
                    },
                ],
                "summary": [
                    {
                        "country": "US",
                        "region": "AZ",
                        "jurisType": "State",
                        "jurisCode": "04",
                        "jurisName": "ARIZONA",
                        "taxAuthorityType": 45,
                        "stateAssignedNo": "",
                        "taxType": "Sales",
                        "taxSubType": "S",
                        "taxName": "AZ STATE TAX",
                        "rateType": "General",
                        "taxable": 320.0,
                        "rate": 0.056,
                        "tax": 17.92,
                        "taxCalculated": 17.92,
                        "nonTaxable": 0.0,
                        "exemption": 0.0,
                    },
                    {
                        "country": "US",
                        "region": "AZ",
                        "jurisType": "County",
                        "jurisCode": "019",
                        "jurisName": "PIMA",
                        "taxAuthorityType": 45,
                        "stateAssignedNo": "PMA",
                        "taxType": "Sales",
                        "taxSubType": "S",
                        "taxName": "AZ COUNTY TAX",
                        "rateType": "General",
                        "taxable": 320.0,
                        "rate": 0.005,
                        "tax": 1.6,
                        "taxCalculated": 1.6,
                        "nonTaxable": 0.0,
                        "exemption": 0.0,
                    },
                ],
            }
            with Form(
                self.env["repair.order"].with_context(lineNumber=999)
            ) as repair_form:
                repair_form.product_id = product_to_repair
                repair_form.partner_id = partner
                repair_form.invoice_method = "b4repair"
                repair_form.location_id = self.stock_warehouse.lot_stock_id
                with repair_form.operations.new() as repair_line:
                    repair_line.product_id = product_to_add
                    repair_line.product_uom_qty = 1
                repair = repair_form.save()
            repair.action_repair_confirm()
            tax = repair.operations.tax_id.filtered(lambda t: t.is_avatax)
            self.assertEqual(round(tax.amount, 2), 6.1)
            repair.action_repair_invoice_create()
            self.assertEqual(
                len(repair.invoice_id), 1, "No invoice exists for this repair order"
            )
            self.assertEqual(repair.invoice_id.exemption_code, "111")
