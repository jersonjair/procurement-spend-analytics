# How I used Python, SQL and an interactive dashboard to analyze $205M in procurement contracts

**By Jerson · Procurement Data Analyst · May 2026**

---

A few weeks ago I asked myself a question every procurement analyst should ask before making any purchasing decision:

> *Do we really know where the money is going?*

The honest answer, in most organizations, is: **not entirely**.

The data exists. It lives in the ERP, in contracts, in emails. But scattered, unstructured, without history. This project was born from wanting to answer that question properly — with data, with code, and with a dashboard any manager can use.

---

## The business problem

Imagine a regional distribution company — let's call it LatamCorp S.A. — operating in Panama with 20 active vendors. Leadership had three suspicions:

1. Spend is concentrated in a few vendors — an operational risk.
2. Some categories are growing unchecked — nobody knows why.
3. There is no visibility into spend over time — decisions are made blind.

My task: build a complete analysis that answers these three questions with real data.

---

## The tech stack

I kept everything simple and intentional. Nothing I can't justify:

- **Python + pandas** — cleaning, transformation, EDA and chart generation
- **SQL con DuckDB** — analytical queries directly on the processed CSV
- **HTML + Chart.js** — standalone interactive dashboard, no server, no Power BI license

The dataset: **4,930 purchase contracts**, FY2022–2023, $205M in total spend.

---

## What I found

### 1. The Pareto problem: 5 vendors, 83% of spend

This was the most critical finding.

Out of 20 active vendors, **only 5 hold 83% of total spend**:

| Vendor | Total Spend | % of Total |
|--------|-------------|-------------|
| Distribuidora Global S.A. | $45.9M | 22.4% |
| TechSupplies Panama | $38.9M | 18.9% |
| Grupo Logístico del Istmo | $30.7M | 15.0% |
| Oficentro Internacional | $29.9M | 14.6% |
| Ferremax Industrial | $25.0M | 12.2% |

This isn't efficiency — it's fragility. Any disruption with one of these vendors (bankruptcy, stockout, price renegotiation) would materially impact operations.

**¿What to do?** Enforce a 15% cap per vendor and develop alternative suppliers in the highest-concentration categories.

---

### 2. The HHI index: sitting at the edge of the risk zone

To measure concentration objectively, I calculated the **Herfindahl-Hirschman Index (HHI)** — the same metric antitrust regulators use..

```sql
WITH shares AS (
    SELECT vendor_name,
           SUM(award_amount) * 100.0 / SUM(SUM(award_amount)) OVER () AS market_share_pct
    FROM procurement
    GROUP BY vendor_name
)
SELECT ROUND(SUM(market_share_pct * market_share_pct), 1) AS HHI_index
FROM shares;
-- Resultado: 1,466.1
```

**HHI = 1,466** — within the "competitive" threshold (< 1,500), but only 34 points from the limit. One additional large contract with Distribuidora Global would push it into moderate concentration territory.

This number should be on every procurement director's dashboard.

---

### 3. IT grew 23% year-over-year. Logistics grew 53%. Why?

The year-over-year analysis revealed two very different patterns:

**Growing categories::**
- Logistics & Transport: **+53%** ($12.6M → $19.3M)
- Medical Supplies: **+27%**
- IT & Technology: **+23%** ($22M → $27.1M)

**Contracting categories:**
- Professional Services: **-17%** ($15.1M → $12.6M)
- Maintenance & Repair: **-11%**

IT growth is expected and positive — it correlates with digitalization initiatives. But the **53% jump in Logistics** in a single year warrants a deeper look: is this real business expansion or inefficiency in the distribution chain?

The drop in Professional Services could be a positive sign of growing internal capacity — or it could signal budget cuts affecting strategic projects.

**Without data, both are just opinions.**

---

### 4. December 2023: the anomalous spike

The monthly trend revealed something unexpected: a peak of $12.5M in December 2023 — the highest of the entire period, 50% above the previous month.

This type of year-end concentration is the classic *"use it or lose it"* budget pattern — a practice that inflates costs, rushes poorly negotiated contracts, and creates operational risk.

**Recomendation:** review high-value contracts awarded in November–December and assess whether the budget planning process allows for better distribution throughout the year.

---

## The technical part I enjoyed most: SQL with window functions

One of the most satisfying parts of the project was writing the analytical queries. Here's the one that calculates the Pareto cumulative directly in SQL:

```sql
SELECT
    vendor_name,
    ROUND(SUM(award_amount), 2) AS total_spend,
    ROUND(SUM(award_amount) * 100.0
          / SUM(SUM(award_amount)) OVER (), 2) AS pct_of_total,
    ROUND(SUM(SUM(award_amount)) OVER (
          ORDER BY SUM(award_amount) DESC
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
          * 100.0 / SUM(SUM(award_amount)) OVER (), 2) AS cumulative_pct
FROM procurement
GROUP BY vendor_name
ORDER BY total_spend DESC;
```

No Python needed. Pure SQL, with a nested window function, calculates the cumulative percentage in a single pass. Clean and reproducible.

---

## What I learned building this

**On data:** Dirty data is the norm, not the exception. The dataset had 30 exact duplicates, 158 null amounts, and 38 unique vendor names that after standardizing casing dropped to 20. Cleaning took as long as the analysis itself.

**On business:** Numbers are the starting point, not the destination. An HHI of 1,466 is interesting. The question "what do we do about it?" is where the real value lives.

**On comunication:** A dashboard nobody understands is as useless as having no data at all. I designed the dashboard so a manager with no technical background could read it in 2 minutes and extract concrete decisions.

---

## Resources and code

All the code is available on GitHub — including the cleaning script, 10 documented SQL queries, EDA scripts with 6 visualizations, and the interactive HTML dashboard:

🔗 **GitHub:** `github.com/jersonjair/procurement-spend-analytics`
🔗 **Dashboard:** `jersonjair.github.io/procurement-spend-analytics`

If you work in procurement, supply chain or data analytics and want to discuss the methodology — find me on LinkedIn.

---

*This analysis uses synthetic data generated for portfolio purposes. The methodology is directly applicable to real datasets from PanamaCompra, USAspending.gov, or internal ERP systems.*

---

**Tags:** #DataAnalytics #Procurement #Python #SQL #SupplyChain #PowerBI #DataScience #Panama
