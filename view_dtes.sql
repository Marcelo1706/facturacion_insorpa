SELECT
	FH_PROCESAMIENTO,
	CASE TIPO_DTE
		WHEN '01' THEN 'Factura'
		WHEN '03' THEN 'Comprobante de Crédito Fiscal'
		WHEN '04' THEN 'Nota de Remisión'
		WHEN '05' THEN 'Nota de Crédito'
		WHEN '06' THEN 'Nota de Débito'
		WHEN '07' THEN 'Comprobante de Retención'
		WHEN '11' THEN 'Factura de Exportación'
		WHEN '14' THEN 'Factura de Sujeto Excluido'
		ELSE TIPO_DTE
	END AS TIPO_DOCUMENTO,
	COD_GENERACION,
	NUMERO_CONTROL,
	SELLO_RECIBIDO,
	ESTADO,
	COALESCE(
		(
			SELECT
				AP ->> 'valor'
			FROM
				JSONB_ARRAY_ELEMENTS(DOCUMENTO::JSONB -> 'apendice') AS AP
			WHERE
				AP ->> 'campo' = 'Tienda'
			LIMIT
				1
		),
		''
	) AS TIENDA,
	COALESCE(
		(
			SELECT
				AP ->> 'valor'
			FROM
				JSONB_ARRAY_ELEMENTS(DOCUMENTO::JSONB -> 'apendice') AS AP
			WHERE
				AP ->> 'campo' = 'Transaccion'
			LIMIT
				1
		),
		''
	) AS TRANSACCION,
	COALESCE(
		DOCUMENTO::JSONB -> 'receptor' ->> 'nit',2
		DOCUMENTO::JSONB -> 'receptor' ->> 'numDocumento',
		DOCUMENTO::JSONB -> 'sujetoExcluido' ->> 'numDocumento',
		DOCUMENTO::JSONB -> 'donante' ->> 'numDocumento',
		''
	) AS DOCUMENTO_RECEPTOR,
	COALESCE(
		DOCUMENTO::JSONB -> 'receptor' ->> 'nombre',
		DOCUMENTO::JSONB -> 'sujetoExcluido' ->> 'nombre',
		DOCUMENTO::JSONB -> 'donante' ->> 'nombre',
		''
	) AS NOMBRE_RECEPTOR,
	-- Neto
    CASE TIPO_DTE
        WHEN '01' THEN TO_CHAR((documento::jsonb->'resumen'->>'totalPagar')::numeric, '"$"FM999990.00')
        WHEN '03' THEN TO_CHAR((documento::jsonb->'resumen'->>'subTotalVentas')::numeric, '"$"FM999990.00')
        WHEN '04' THEN TO_CHAR((documento::jsonb->'resumen'->>'subTotalVentas')::numeric, '"$"FM999990.00')
        WHEN '05' THEN TO_CHAR((documento::jsonb->'resumen'->>'subTotalVentas')::numeric, '"$"FM999990.00')
        WHEN '07' THEN TO_CHAR((documento::jsonb->'resumen'->>'totalSujetoRetencion')::numeric, '"$"FM999990.00')
        WHEN '11' THEN TO_CHAR((documento::jsonb->'resumen'->>'totalPagar')::numeric, '"$"FM999990.00')
        WHEN '14' THEN TO_CHAR((documento::jsonb->'resumen'->>'totalCompra')::numeric, '"$"FM999990.00')
        ELSE '$0.00'
    END AS neto,

    -- IVA
    CASE TIPO_DTE
        WHEN '03' THEN TO_CHAR(((documento::jsonb->'resumen'->>'subTotalVentas')::numeric * 0.13), '"$"FM999990.00')
        WHEN '04' THEN TO_CHAR(((documento::jsonb->'resumen'->>'subTotalVentas')::numeric * 0.13), '"$"FM999990.00')
        WHEN '05' THEN TO_CHAR(((documento::jsonb->'resumen'->>'subTotalVentas')::numeric * 0.13), '"$"FM999990.00')
        WHEN '07' THEN TO_CHAR((documento::jsonb->'resumen'->>'totalIVAretenido')::numeric, '"$"FM999990.00')
        ELSE '$0.00'
    END AS iva,

    -- Total
    CASE TIPO_DTE
        WHEN '01' THEN TO_CHAR((documento::jsonb->'resumen'->>'totalPagar')::numeric, '"$"FM999990.00')
        WHEN '03' THEN TO_CHAR((documento::jsonb->'resumen'->>'totalPagar')::numeric, '"$"FM999990.00')
        WHEN '04' THEN TO_CHAR((documento::jsonb->'resumen'->>'montoTotalOperacion')::numeric, '"$"FM999990.00')
        WHEN '05' THEN TO_CHAR((documento::jsonb->'resumen'->>'montoTotalOperacion')::numeric, '"$"FM999990.00')
        WHEN '07' THEN TO_CHAR((documento::jsonb->'resumen'->>'totalSujetoRetencion')::numeric, '"$"FM999990.00')
        WHEN '11' THEN TO_CHAR((documento::jsonb->'resumen'->>'totalPagar')::numeric, '"$"FM999990.00')
        WHEN '14' THEN TO_CHAR((documento::jsonb->'resumen'->>'totalCompra')::numeric, '"$"FM999990.00')
        ELSE '$0.00'
    END AS total,
	CASE 
		WHEN OBSERVACIONES = '[]' THEN NULL 
		ELSE OBSERVACIONES 
	END AS OBSERVACIONES,
	ENLACE_PDF,
	ENLACE_JSON,
	ENLACE_TICKET
FROM
	PUBLIC.DTE_GENERADOS
LIMIT 100;