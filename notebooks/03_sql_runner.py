# ==============================================================
# LatamCorp S.A. — Procurement Spend Analytics
# Fase 4: Ejecución de Consultas SQL (DuckDB)
# Autor: Jerson | Procurement Data Analyst
# ==============================================================

import duckdb
import pandas as pd
import os

OUT_DIR = "../data/processed/sql_results"
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("FASE 4 — CONSULTAS SQL (DuckDB sobre CSV)")
print("=" * 60)

# ── Conexión y registro de tabla virtual ──────────────────────
con = duckdb.connect()
con.execute("""
    CREATE VIEW procurement AS
    SELECT * FROM read_csv_auto('../data/processed/latamcorp_procurement_clean.csv',
                                 header=True, dateformat='%Y-%m-%d')
""")
print("\n[OK] Tabla 'procurement' registrada en DuckDB")

# ── Definición de queries ─────────────────────────────────────
queries = {
    "Q01_executive_summary": """
        SELECT
            COUNT(*)                                        AS total_contracts,
            COUNT(DISTINCT vendor_name)                     AS unique_vendors,
            ROUND(SUM(award_amount), 2)                     AS total_spend_usd,
            ROUND(AVG(award_amount), 2)                     AS avg_contract_usd,
            ROUND(MEDIAN(award_amount), 2)                  AS median_contract_usd,
            ROUND(MAX(award_amount), 2)                     AS max_contract_usd
        FROM procurement
    """,

    "Q02_spend_by_category": """
        SELECT
            category,
            COUNT(*)                                            AS contracts,
            ROUND(SUM(award_amount), 2)                         AS total_spend,
            ROUND(AVG(award_amount), 2)                         AS avg_spend,
            ROUND(SUM(award_amount) * 100.0
                  / SUM(SUM(award_amount)) OVER (), 2)          AS pct_of_total
        FROM procurement
        GROUP BY category
        ORDER BY total_spend DESC
    """,

    "Q03_pareto_vendors": """
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
        LIMIT 10
    """,

    "Q04_monthly_mom_change": """
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
        FROM monthly
    """,

    "Q05_dept_by_year": """
        SELECT
            department,
            fiscal_year,
            COUNT(*)                            AS contracts,
            ROUND(SUM(award_amount), 2)         AS total_spend,
            ROUND(AVG(award_amount), 2)         AS avg_spend
        FROM procurement
        GROUP BY department, fiscal_year
        ORDER BY department, fiscal_year
    """,

    "Q06_high_value_contracts": """
        SELECT
            award_id,
            CAST(award_date AS VARCHAR)         AS award_date,
            vendor_name,
            category,
            department,
            ROUND(award_amount, 2)              AS award_amount,
            contract_type
        FROM procurement
        WHERE is_high_value = TRUE
        ORDER BY award_amount DESC
        LIMIT 20
    """,

    "Q07_hhi_concentration": """
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
        FROM shares
    """,

    "Q08_contract_type_analysis": """
        SELECT
            contract_type,
            COUNT(*)                            AS contracts,
            ROUND(SUM(award_amount), 2)         AS total_spend,
            ROUND(AVG(award_amount), 2)         AS avg_spend,
            ROUND(SUM(award_amount) * 100.0
                  / SUM(SUM(award_amount)) OVER (), 2) AS pct_of_total
        FROM procurement
        GROUP BY contract_type
        ORDER BY total_spend DESC
    """,

    "Q09_single_contract_vendors": """
        SELECT
            vendor_name,
            country,
            category,
            ROUND(SUM(award_amount), 2) AS total_spend,
            COUNT(*)                    AS contract_count
        FROM procurement
        GROUP BY vendor_name, country, category
        HAVING COUNT(*) = 1
        ORDER BY total_spend DESC
    """,

    "Q10_yoy_by_category": """
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
        ORDER BY yoy_change_pct DESC
    """,
}

# ── Ejecutar todas las queries ────────────────────────────────
for name, sql in queries.items():
    print(f"\n{'─'*55}")
    print(f"  {name}")
    print(f"{'─'*55}")
    df = con.execute(sql).df()
    print(df.to_string(index=False))
    df.to_csv(f"{OUT_DIR}/{name}.csv", index=False)
    print(f"  → Exportado: sql_results/{name}.csv")

con.close()
print(f"\n\n✅ Fase 4 completada. {len(queries)} queries ejecutadas y exportadas.")
print(f"   Resultados en: data/processed/sql_results/")
