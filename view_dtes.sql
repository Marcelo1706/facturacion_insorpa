CREATE OR REPLACE FUNCTION get_dtes_filtrados(
    p_fecha_inicio TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_fecha_fin TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_estado VARCHAR(255) DEFAULT NULL,
    p_tienda TEXT DEFAULT NULL,
    p_documento_receptor TEXT DEFAULT NULL,
    p_nombre_receptor TEXT DEFAULT NULL,
    p_cod_generacion VARCHAR(255) DEFAULT NULL,
    p_sello_recibido VARCHAR(255) DEFAULT NULL,
    p_numero_control VARCHAR(255) DEFAULT NULL,
    p_total_min NUMERIC DEFAULT NULL,
    p_total_max NUMERIC DEFAULT NULL
)
RETURNS TABLE (
    cod_generacion VARCHAR(255),
    tipo_dte VARCHAR(255),
    documento_receptor TEXT,
    nombre_receptor TEXT,
    sello_recibido VARCHAR(255),
    numero_control VARCHAR(255),
    fh_procesamiento TIMESTAMP WITH TIME ZONE,
    observaciones TEXT,
    enlace_pdf VARCHAR(255),
    enlace_json VARCHAR(255),
    enlace_ticket VARCHAR(255),
    estado VARCHAR(255),
    tienda TEXT,
    transaccion TEXT,
    neto TEXT,
    iva TEXT,
    total TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        dg.cod_generacion,
        dg.tipo_dte,
        dg.documento::jsonb->'receptor'->>'numDocumento' AS documento_receptor,
        dg.documento::jsonb->'receptor'->>'nombre' AS nombre_receptor,
        dg.sello_recibido,
        dg.numero_control,
        dg.fh_procesamiento,
        dg.observaciones,
        dg.enlace_pdf,
        dg.enlace_json,
        dg.enlace_ticket,
        dg.estado,

        -- Apendice tienda y transacción
        (
            SELECT apendice_item->>'valor'
            FROM jsonb_array_elements(dg.documento::jsonb->'apendice') AS apendice_item
            WHERE apendice_item->>'campo' = 'Tienda'
            LIMIT 1
        ) AS tienda,
        (
            SELECT apendice_item->>'valor'
            FROM jsonb_array_elements(dg.documento::jsonb->'apendice') AS apendice_item
            WHERE apendice_item->>'campo' = 'Transaccion'
            LIMIT 1
        ) AS transaccion,     -- Neto
        CASE dg.tipo_dte
            WHEN '01' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'totalPagar')::numeric, '"$"FM999990.00')
            WHEN '03' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'subTotalVentas')::numeric, '"$"FM999990.00')
            WHEN '04' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'subTotalVentas')::numeric, '"$"FM999990.00')
            WHEN '05' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'subTotalVentas')::numeric, '"$"FM999990.00')
            WHEN '07' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'totalSujetoRetencion')::numeric, '"$"FM999990.00')
            WHEN '11' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'totalPagar')::numeric, '"$"FM999990.00')
            WHEN '14' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'totalCompra')::numeric, '"$"FM999990.00')
            ELSE '$0.00'
        END AS neto,

        -- IVA
        CASE dg.tipo_dte
            WHEN '03' THEN TO_CHAR(((dg.documento::jsonb->'resumen'->>'subTotalVentas')::numeric * 0.13), '"$"FM999990.00')
            WHEN '04' THEN TO_CHAR(((dg.documento::jsonb->'resumen'->>'subTotalVentas')::numeric * 0.13), '"$"FM999990.00')
            WHEN '05' THEN TO_CHAR(((dg.documento::jsonb->'resumen'->>'subTotalVentas')::numeric * 0.13), '"$"FM999990.00')
            WHEN '07' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'totalIVAretenido')::numeric, '"$"FM999990.00')
            ELSE '$0.00'
        END AS iva,

        -- Total
        CASE dg.tipo_dte
            WHEN '01' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'totalPagar')::numeric, '"$"FM999990.00')
            WHEN '03' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'totalPagar')::numeric, '"$"FM999990.00')
            WHEN '04' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'montoTotalOperacion')::numeric, '"$"FM999990.00')
            WHEN '05' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'montoTotalOperacion')::numeric, '"$"FM999990.00')
            WHEN '07' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'totalSujetoRetencion')::numeric, '"$"FM999990.00')
            WHEN '11' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'totalPagar')::numeric, '"$"FM999990.00')
            WHEN '14' THEN TO_CHAR((dg.documento::jsonb->'resumen'->>'totalCompra')::numeric, '"$"FM999990.00')
            ELSE '$0.00'
        END AS total

    FROM dte_generados dg
    WHERE 
        (p_fecha_inicio IS NULL OR dg.fh_procesamiento >= p_fecha_inicio)
        AND (p_fecha_fin IS NULL OR dg.fh_procesamiento <= p_fecha_fin)
        AND (p_estado IS NULL OR p_estado = 'TODOS' OR dg.estado = p_estado)
        AND (
            p_tienda IS NULL OR EXISTS (
                SELECT 1
                FROM jsonb_array_elements(dg.documento::jsonb->'apendice') AS apendice_item
                WHERE apendice_item->>'campo' = 'Tienda'
                  AND apendice_item->>'valor' ILIKE '%' || p_tienda || '%'
            )
        )
        AND (p_documento_receptor IS NULL OR dg.documento::jsonb->'receptor'->>'numDocumento' ILIKE '%' || p_documento_receptor || '%')
        AND (p_nombre_receptor IS NULL OR dg.documento::jsonb->'receptor'->>'nombre' ILIKE '%' || p_nombre_receptor || '%')
        AND (p_cod_generacion IS NULL OR dg.cod_generacion ILIKE '%' || p_cod_generacion || '%')
        AND (p_sello_recibido IS NULL OR dg.sello_recibido ILIKE '%' || p_sello_recibido || '%')
        AND (p_numero_control IS NULL OR dg.numero_control ILIKE '%' || p_numero_control || '%')
        AND (
            p_total_min IS NULL 
            OR (
                CASE dg.tipo_dte
                    WHEN '01' THEN (dg.documento::jsonb->'resumen'->>'totalPagar')::numeric
                    WHEN '03' THEN (dg.documento::jsonb->'resumen'->>'totalPagar')::numeric
                    WHEN '04' THEN (dg.documento::jsonb->'resumen'->>'montoTotalOperacion')::numeric
                    WHEN '05' THEN (dg.documento::jsonb->'resumen'->>'montoTotalOperacion')::numeric
                    WHEN '07' THEN (dg.documento::jsonb->'resumen'->>'totalSujetoRetencion')::numeric
                    WHEN '11' THEN (dg.documento::jsonb->'resumen'->>'totalPagar')::numeric
                    WHEN '14' THEN (dg.documento::jsonb->'resumen'->>'totalCompra')::numeric
                    ELSE 0
                END >= p_total_min
            )
        )
        AND (
            p_total_max IS NULL 
            OR (
                CASE dg.tipo_dte
                    WHEN '01' THEN (dg.documento::jsonb->'resumen'->>'totalPagar')::numeric
                    WHEN '03' THEN (dg.documento::jsonb->'resumen'->>'totalPagar')::numeric
                    WHEN '04' THEN (dg.documento::jsonb->'resumen'->>'montoTotalOperacion')::numeric
                    WHEN '05' THEN (dg.documento::jsonb->'resumen'->>'montoTotalOperacion')::numeric
                    WHEN '07' THEN (dg.documento::jsonb->'resumen'->>'totalSujetoRetencion')::numeric
                    WHEN '11' THEN (dg.documento::jsonb->'resumen'->>'totalPagar')::numeric
                    WHEN '14' THEN (dg.documento::jsonb->'resumen'->>'totalCompra')::numeric
                    ELSE 0
                END <= p_total_max
            )
        );
END;
$$ LANGUAGE plpgsql;
