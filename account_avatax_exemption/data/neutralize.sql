-- The exemption exports have gates of their own, independent from
-- disable_tax_calculation, and /exemption/<id> is a public route.
UPDATE avalara_salestax
SET tax_item_export = false,
    exemption_export = false,
    exemption_rule_export = false;
