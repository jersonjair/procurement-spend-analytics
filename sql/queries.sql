-- ==============================================================
-- LatamCorp S.A. — Procurement Spend Analytics
-- Fase 4: Consultas SQL
-- Base de datos: DuckDB (sobre CSV procesado)
-- Autor: Jerson | Procurement Data Analyst
-- ==============================================================


-- ─────────────────────────────────────────────────────────────
-- Q01 — RESUMEN EJECUTIVO GENERAL
-- KPIs de alto nivel: gasto total, contratos, vendors, promedio
-- ─────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                        AS total_contracts,
    COUNT(DISTINCT vendor_name)                     AS unique_vendors,
    ROUND(SUM(award_amount), 2)                     AS total_spend_usd,
    ROUND(AVG(award_amount), 2)                     AS avg_contract_usd,
    ROUND(MEDIAN(award_amount), 2)                  AS median_contract_usd,
    ROUND(MAX(award_amount), 2)                     AS max_contract_usd
FROM procurement;


-- ─────────────────────────────────────────────────────────────
-- Q02 — GASTO TOTAL POR CATEGORÍA (ordenado desc)
-- Identifica las categorías que concentran más presupuesto
-- ─────────────────────────────────────────────────────────────
SELECT
    category,
    COUNT(*)                                            AS contracts,
    ROUND(SUM(award_amount), 2)                         AS total_spend,
    ROUND(AVG(award_amount), 2)                         AS avg_spend,
    ROUND(SUM(award_amount) * 100.0
          / SUM(SUM(award_amount)) OVER (), 2)          AS pct_of_total
FROM procurement
GROUP BY category
ORDER BY total_spend DESC;


-- ─────────────────────────────────────────────────────────────
-- Q03 — TOP 10 PROVEEDORES POR GASTO (PARETO)
-- Los 5 primeros concentran ~83% del gasto total
-- ─────────────────────────────────────────────────────────────
SELECT
    vendor_name,
    COUNT(*)                                            AS contracts,
    ROUND(SUM(award_amount), 2)                         AS total_spend,
    ROUND(SUM(award_amount) * 100.0
          / SUM(SUM(award_amount)) OVER (), 2)          AS pct_of_total,
    ROUND(SUM(SUM(award_amount)) OVER (
          ORDER BY SUM(award_amount) DESC
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
          * 100.0 / SUM(SUM(award_amount)) OVER (), 2)  AS cumulative_pct
FROM procurement
GROUP BY vendor_name
ORDER BY total_spend DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────
-- Q04 — GASTO MENSUAL Y VARIACIÓN MES A MES
-- Detecta picos, caídas y estacionalidad en el gasto
-- ─────────────────────────────────────────────────────────────
WITH monthly AS (
    SELECT
        STRFTIME(CAST(award_date AS DATE), '%Y-%m') AS month_year,
        ROUND(SUM(award_amount), 2)                 AS monthly_spend
    FROM procurement
    GROUP BY STRFTIME(CAST(award_date AS DATE), '%Y-%m')
    ORDER BY month_year
)
SELECT
    month_year,
    monthly_spend,
    LAG(monthly_spend) OVER (ORDER BY month_year) AS prev_month_spend,
    ROUND(
        (monthly_spend - LAG(monthly_spend) OVER (ORDER BY month_year))
        * 100.0
        / NULLIF(LAG(monthly_spend) OVER (ORDER BY month_year), 0),
    2) AS mom_change_pct
FROM monthly;


-- ─────────────────────────────────────────────────────────────
-- Q05 — GASTO POR DEPARTAMENTO Y AÑO FISCAL
-- Permite comparar el comportamiento de cada área entre 2022 y 2023
-- ─────────────────────────────────────────────────────────────
SELECT
    department,
    fiscal_year,
    COUNT(*)                            AS contracts,
    ROUND(SUM(award_amount), 2)         AS total_spend,
    ROUND(AVG(award_amount), 2)         AS avg_spend
FROM procurement
GROUP BY department, fiscal_year
ORDER BY department, fiscal_year;


-- ─────────────────────────────────────────────────────────────
-- Q06 — CONTRATOS DE ALTO VALOR (TOP 10% — P90)
-- Contratos estratégicos que requieren mayor atención de gestión
-- ─────────────────────────────────────────────────────────────
SELECT
    award_id,
    award_date,
    vendor_name,
    category,
    department,
    ROUND(award_amount, 2)  AS award_amount,
    contract_type
FROM procurement
WHERE is_high_value = TRUE
ORDER BY award_amount DESC
LIMIT 20;


-- ─────────────────────────────────────────────────────────────
-- Q07 — CONCENTRACIÓN DE GASTO POR PROVEEDOR (HHI)
-- Índice Herfindahl-Hirschman: mide riesgo de concentración
-- < 1,500 = competitivo | 1,500–2,500 = moderado | > 2,500 = concentrado
-- ─────────────────────────────────────────────────────────────
WITH shares AS (
    SELECT
        vendor_name,
        SUM(award_amount) * 100.0 / SUM(SUM(award_amount)) OVER () AS market_share_pct
    FROM procurement
    GROUP BY vendor_name
)
SELECT
    ROUND(SUM(market_share_pct * market_share_pct), 1)  AS HHI_index,
    CASE
        WHEN SUM(market_share_pct * market_share_pct) < 1500  THEN 'Competitivo'
        WHEN SUM(market_share_pct * market_share_pct) < 2500  THEN 'Moderadamente concentrado'
        ELSE                                                        'Altamente concentrado'
    END                                                  AS hhi_interpretation
FROM shares;


-- ─────────────────────────────────────────────────────────────
-- Q08 — TIPO DE CONTRATO: DISTRIBUCIÓN Y GASTO PROMEDIO
-- Muestra si el uso de Framework Agreements vs Spot Purchase
-- impacta el costo promedio por contrato
-- ─────────────────────────────────────────────────────────────
SELECT
    contract_type,
    COUNT(*)                            AS contracts,
    ROUND(SUM(award_amount), 2)         AS total_spend,
    ROUND(AVG(award_amount), 2)         AS avg_spend,
    ROUND(SUM(award_amount) * 100.0
          / SUM(SUM(award_amount)) OVER (), 2) AS pct_of_total
FROM procurement
GROUP BY contract_type
ORDER BY total_spend DESC;


-- ─────────────────────────────────────────────────────────────
-- Q09 — PROVEEDORES CON SOLO 1 CONTRATO (RIESGO DE DEPENDENCIA)
-- Vendedores poco probados; riesgo para contratos futuros
-- ─────────────────────────────────────────────────────────────
SELECT
    vendor_name,
    country,
    category,
    ROUND(SUM(award_amount), 2) AS total_spend,
    COUNT(*)                    AS contract_count
FROM procurement
GROUP BY vendor_name, country, category
HAVING COUNT(*) = 1
ORDER BY total_spend DESC;


-- ─────────────────────────────────────────────────────────────
-- Q10 — COMPARATIVO FY2022 vs FY2023 POR CATEGORÍA
-- Variación interanual del gasto por área de compra
-- ─────────────────────────────────────────────────────────────
SELECT
    category,
    ROUND(SUM(CASE WHEN fiscal_year = 2022 THEN award_amount END), 2) AS spend_2022,
    ROUND(SUM(CASE WHEN fiscal_year = 2023 THEN award_amount END), 2) AS spend_2023,
    ROUND(
        (SUM(CASE WHEN fiscal_year = 2023 THEN award_amount END)
         - SUM(CASE WHEN fiscal_year = 2022 THEN award_amount END))
        * 100.0
        / NULLIF(SUM(CASE WHEN fiscal_year = 2022 THEN award_amount END), 0),
    2) AS yoy_change_pct
FROM procurement
GROUP BY category
ORDER BY yoy_change_pct DESC;
