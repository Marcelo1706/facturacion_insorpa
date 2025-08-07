SELECT DISTINCT apendice_item->>'valor' AS tienda
FROM dte_generados dg,
    jsonb_array_elements(dg.documento::jsonb->'apendice') AS apendice_item
WHERE apendice_item->>'campo' = 'Tienda'
ORDER BY tienda;
