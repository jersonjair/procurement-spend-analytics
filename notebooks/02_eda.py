# ==============================================================
# LatamCorp S.A. — Procurement Spend Analytics
# Fase 3: Análisis Exploratorio de Datos (EDA)
# Autor: Jerson | Procurement Data Analyst
# ==============================================================

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os
warnings.filterwarnings('ignore')

# ── Estilo global ──────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="Blues_d")
plt.rcParams.update({
    "figure.facecolor": "#F8F9FA",
    "axes.facecolor":   "#F8F9FA",
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   13,
    "axes.labelsize":   11,
})
ACCENT   = "#1B4F8A"
ACCENT2  = "#E8534A"
GREY     = "#6C757D"
OUT_DIR  = "../data/processed/charts"
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("FASE 3 — ANÁLISIS EXPLORATORIO DE DATOS (EDA)")
print("=" * 60)

# ─────────────────────────────────────────────
# 1. CARGA
# ─────────────────────────────────────────────
df = pd.read_csv("../data/processed/latamcorp_procurement_clean.csv",
                 parse_dates=["award_date"])
print(f"\n[1] Dataset cargado: {df.shape[0]:,} filas · {df.shape[1]} columnas")

# ─────────────────────────────────────────────
# 2. ESTADÍSTICAS DESCRIPTIVAS
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("[2] ESTADÍSTICAS DESCRIPTIVAS")
print("=" * 60)

total_spend  = df["award_amount"].sum()
avg_contract = df["award_amount"].mean()
median_contract = df["award_amount"].median()
n_vendors    = df["vendor_name"].nunique()
n_contracts  = len(df)

print(f"\n  Gasto total          : ${total_spend:>15,.2f}")
print(f"  Contratos totales    : {n_contracts:>15,}")
print(f"  Vendors únicos       : {n_vendors:>15,}")
print(f"  Promedio / contrato  : ${avg_contract:>15,.2f}")
print(f"  Mediana / contrato   : ${median_contract:>15,.2f}")
print(f"  Contrato máximo      : ${df['award_amount'].max():>15,.2f}")
print(f"  Contrato mínimo      : ${df['award_amount'].min():>15,.2f}")

# ─────────────────────────────────────────────
# 3. GASTO POR CATEGORÍA
# ─────────────────────────────────────────────
print("\n[3] Gasto por Categoría")
cat_spend = (df.groupby("category")["award_amount"]
               .agg(total="sum", contracts="count", avg="mean")
               .sort_values("total", ascending=False))
cat_spend["pct"] = cat_spend["total"] / total_spend * 100
print(cat_spend.assign(
    total=cat_spend["total"].map("${:,.0f}".format),
    avg=cat_spend["avg"].map("${:,.0f}".format),
    pct=cat_spend["pct"].map("{:.1f}%".format)
).to_string())

fig, ax = plt.subplots(figsize=(10, 5))
colors = [ACCENT if i == 0 else "#5B9BD5" if i < 3 else "#A8C8E8"
          for i in range(len(cat_spend))]
bars = ax.barh(cat_spend.index[::-1], cat_spend["total"][::-1], color=colors[::-1])
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
for bar, val in zip(bars, cat_spend["total"][::-1]):
    ax.text(bar.get_width() + total_spend * 0.002, bar.get_y() + bar.get_height()/2,
            f"${val/1e6:.1f}M", va="center", fontsize=9, color=GREY)
ax.set_title("Gasto Total por Categoría — LatamCorp FY2022-23", fontweight="bold", pad=12)
ax.set_xlabel("Gasto Total (USD)")
ax.set_xlim(0, cat_spend["total"].max() * 1.15)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/01_spend_by_category.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → Gráfico guardado: 01_spend_by_category.png")

# ─────────────────────────────────────────────
# 4. TOP 10 PROVEEDORES (PARETO)
# ─────────────────────────────────────────────
print("\n[4] Top Proveedores + Análisis Pareto")
vendor_spend = (df.groupby("vendor_name")["award_amount"]
                  .sum().sort_values(ascending=False))
vendor_spend_pct = vendor_spend / total_spend * 100
cumulative      = vendor_spend_pct.cumsum()
pareto_80_idx   = (cumulative <= 80).sum() + 1
print(f"\n  Vendors que acumulan el 80% del gasto: {pareto_80_idx}")
print(f"\n  Top 10 por gasto:")
top10 = vendor_spend.head(10)
for v, amt in top10.items():
    print(f"    {v:<35} ${amt:>12,.0f}  ({amt/total_spend*100:.1f}%)")

fig, ax1 = plt.subplots(figsize=(12, 5))
ax2 = ax1.twinx()
top10_names = [n[:25] + "…" if len(n) > 25 else n for n in top10.index]
bar_colors  = [ACCENT2 if i < pareto_80_idx else ACCENT for i in range(len(top10))]
ax1.bar(range(len(top10)), top10.values, color=bar_colors, alpha=0.85)
ax1.set_xticks(range(len(top10)))
ax1.set_xticklabels(top10_names, rotation=35, ha="right", fontsize=9)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
ax1.set_ylabel("Gasto Total (USD)", color=ACCENT)
cum_top10 = cumulative.head(10).values
ax2.plot(range(len(top10)), cum_top10, color="#E8534A", marker="o", linewidth=2)
ax2.axhline(80, color=GREY, linestyle="--", linewidth=1, label="80%")
ax2.set_ylabel("Acumulado (%)", color=ACCENT2)
ax2.set_ylim(0, 105)
ax1.set_title("Pareto de Proveedores — Top 10 por Gasto", fontweight="bold", pad=12)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/02_pareto_vendors.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → Gráfico guardado: 02_pareto_vendors.png")

# ─────────────────────────────────────────────
# 5. TENDENCIA MENSUAL DE GASTO
# ─────────────────────────────────────────────
print("\n[5] Tendencia Mensual de Gasto")
monthly = (df.groupby("month_year")["award_amount"]
             .sum().reset_index()
             .rename(columns={"award_amount": "total"}))
monthly["month_year"] = pd.PeriodIndex(monthly["month_year"], freq="M")
monthly = monthly.sort_values("month_year")

fig, ax = plt.subplots(figsize=(13, 4))
ax.fill_between(range(len(monthly)), monthly["total"], alpha=0.18, color=ACCENT)
ax.plot(range(len(monthly)), monthly["total"], color=ACCENT, linewidth=2.5, marker="o", markersize=4)
ax.set_xticks(range(len(monthly)))
ax.set_xticklabels([str(p) for p in monthly["month_year"]], rotation=45, ha="right", fontsize=8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
max_idx = monthly["total"].idxmax()
ax.annotate(f"Pico: ${monthly['total'].max()/1e6:.1f}M",
            xy=(monthly.index.get_loc(max_idx), monthly["total"].max()),
            xytext=(monthly.index.get_loc(max_idx) - 2, monthly["total"].max() * 1.05),
            arrowprops=dict(arrowstyle="->", color=ACCENT2),
            color=ACCENT2, fontsize=9)
ax.set_title("Tendencia Mensual de Gasto — FY2022-2023", fontweight="bold", pad=12)
ax.set_ylabel("Gasto Mensual (USD)")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/03_monthly_trend.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → Gráfico guardado: 03_monthly_trend.png")

# ─────────────────────────────────────────────
# 6. GASTO POR DEPARTAMENTO
# ─────────────────────────────────────────────
print("\n[6] Gasto por Departamento")
dept_spend = df.groupby("department")["award_amount"].sum().sort_values(ascending=False)
print(dept_spend.map("${:,.0f}".format).to_string())

fig, ax = plt.subplots(figsize=(9, 5))
palette = sns.color_palette("Blues_d", len(dept_spend))
ax.bar(dept_spend.index, dept_spend.values, color=palette[::-1])
ax.set_xticklabels(dept_spend.index, rotation=35, ha="right", fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
ax.set_title("Gasto Total por Departamento", fontweight="bold", pad=12)
ax.set_ylabel("Gasto Total (USD)")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/04_spend_by_department.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → Gráfico guardado: 04_spend_by_department.png")

# ─────────────────────────────────────────────
# 7. CONCENTRACIÓN DE GASTO — ÍNDICE HHI
# ─────────────────────────────────────────────
print("\n[7] Índice de Concentración HHI (Herfindahl-Hirschman)")
market_shares = (vendor_spend / total_spend * 100)
HHI = (market_shares ** 2).sum()
print(f"\n  HHI = {HHI:,.1f}")
if HHI < 1500:
    hhi_label = "Mercado competitivo (HHI < 1,500)"
elif HHI < 2500:
    hhi_label = "Mercado moderadamente concentrado (1,500–2,500)"
else:
    hhi_label = "Mercado altamente concentrado (HHI > 2,500)"
print(f"  Interpretación: {hhi_label}")

# ─────────────────────────────────────────────
# 8. DISTRIBUCIÓN DE CONTRATOS POR SPEND RANGE
# ─────────────────────────────────────────────
print("\n[8] Distribución por Spend Range")
sr_order = ["Micro (<1K)", "Small (1K-10K)", "Medium (10K-50K)", "Large (50K-200K)", "Strategic (>200K)"]
sr_counts = df["spend_range"].value_counts().reindex(sr_order)
sr_spend  = df.groupby("spend_range")["award_amount"].sum().reindex(sr_order)
print(sr_counts.to_string())

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
pal = sns.color_palette("Blues_d", len(sr_order))
axes[0].bar(sr_order, sr_counts.values, color=pal[::-1])
axes[0].set_title("Nº Contratos por Rango", fontweight="bold")
axes[0].set_xticklabels(sr_order, rotation=30, ha="right", fontsize=8)
axes[0].set_ylabel("Cantidad")
axes[1].bar(sr_order, sr_spend.values, color=pal[::-1])
axes[1].set_title("Gasto Total por Rango", fontweight="bold")
axes[1].set_xticklabels(sr_order, rotation=30, ha="right", fontsize=8)
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
axes[1].set_ylabel("Gasto Total (USD)")
plt.suptitle("Distribución de Contratos por Spend Range", fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/05_spend_range.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → Gráfico guardado: 05_spend_range.png")

# ─────────────────────────────────────────────
# 9. HEATMAP — CATEGORÍA × DEPARTAMENTO
# ─────────────────────────────────────────────
print("\n[9] Heatmap Categoría × Departamento")
heatmap_data = df.pivot_table(values="award_amount", index="category",
                               columns="department", aggfunc="sum", fill_value=0) / 1e6
fig, ax = plt.subplots(figsize=(13, 6))
sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="Blues",
            linewidths=0.4, ax=ax, cbar_kws={"label": "Gasto (USD M)"})
ax.set_title("Gasto (USD M) por Categoría × Departamento", fontweight="bold", pad=12)
ax.set_xlabel("")
ax.set_ylabel("")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/06_heatmap_cat_dept.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → Gráfico guardado: 06_heatmap_cat_dept.png")

# ─────────────────────────────────────────────
# 10. EXPORTAR RESUMEN EDA
# ─────────────────────────────────────────────
summary = {
    "total_spend_usd":      round(total_spend, 2),
    "total_contracts":      n_contracts,
    "unique_vendors":       n_vendors,
    "avg_contract_usd":     round(avg_contract, 2),
    "median_contract_usd":  round(median_contract, 2),
    "pareto_80pct_vendors": int(pareto_80_idx),
    "HHI_index":            round(HHI, 1),
    "HHI_interpretation":   hhi_label,
    "top_category":         cat_spend.index[0],
    "top_vendor":           vendor_spend.index[0],
    "top_department":       dept_spend.index[0],
}
pd.Series(summary).to_csv("../data/processed/eda_summary.csv", header=["value"])
print(f"\n[10] Resumen EDA exportado: data/processed/eda_summary.csv")
print(f"     Gráficos guardados en: data/processed/charts/ ({len(os.listdir(OUT_DIR))} archivos)")
print("\n✅ Fase 3 completada exitosamente.")
