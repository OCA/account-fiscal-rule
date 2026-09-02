-- Leave AvaTax inert: no calculation, no document recording, no usable credentials.
-- account_number keeps a per-row unique value (account_number_company_uniq).
UPDATE avalara_salestax
SET disable_tax_calculation = true,
    disable_tax_reporting = true,
    account_number = 'NEUTRALIZED-' || id::text,
    license_key = '';
