# ==============================================================
# LatamCorp S.A. — Procurement Spend Analytics
# Fase 2: Limpieza y Preparación de Datos
# Autor: Jerson | Procurement Data Analyst
# ==============================================================

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("FASE 2 — LIMPIEZA Y PREPARACIÓN DE DATOS")
print("=" * 60)

# ─────────────────────────────────────────────
# 1. CARGA DE DATOS
# ─────────────────────────────────────────────
df = pd.read_csv("../data/raw/latamcorp_procurement_raw.csv")

print(f"\n[1] Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
print(f"\nColumnas: {list(df.columns)}")
print(f"\nTipos de datos:\n{df.dtypes}")
print(f"\nPrimeras 5 filas:\n{df.head()}")

# ─────────────────────────────────────────────
# 2. DIAGNÓSTICO INICIAL
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("[2] DIAGNÓSTICO INICIAL")
print("=" * 60)

print(f"\nValores nulos por columna:")
print(df.isnull().sum())

print(f"\nDuplicados exactos: {df.duplicated().sum()}")

print(f"\nEstadísticas de award_amount:")
print(df['award_amount'].describe())

print(f"\nVendors únicos antes de limpiar: {df['vendor_name'].nunique()}")

# ─────────────────────────────────────────────
# 3. LIMPIEZA
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("[3] PROCESO DE LIMPIEZA")
print("=" * 60)

df_clean = df.copy()

# 3.1 Eliminar duplicados exactos
before = len(df_clean)
df_clean = df_clean.drop_duplicates()
print(f"\n3.1 Duplicados eliminados: {before - len(df_clean)}")

# 3.2 Estandarizar vendor_name (Title Case, strip espacios)
df_clean['vendor_name'] = df_clean['vendor_name'].str.strip().str.title()
print(f"3.2 vendor_name estandarizado a Title Case")
print(f"    Vendors únicos después: {df_clean['vendor_name'].nunique()}")

# 3.3 Convertir award_date a datetime
df_clean['award_date'] = pd.to_datetime(df_clean['award_date'], errors='coerce')
print(f"3.3 award_date convertida a datetime")

# 3.4 Imputar award_amount nulos con mediana por categoría
median_by_cat = df_clean.groupby('category')['award_amount'].median()
def fill_amount(row):
    if pd.isnull(row['award_amount']):
        return median_by_cat.get(row['category'], df_clean['award_amount'].median())
    return row['award_amount']

df_clean['award_amount'] = df_clean.apply(fill_amount, axis=1)
print(f"3.4 award_amount nulos imputados con mediana por categoría")

# 3.5 Imputar fiscal_year desde award_date
df_clean['fiscal_year'] = df_clean['award_date'].dt.year
# Para filas con award_date nula, usar moda
mode_year = df_clean['fiscal_year'].mode()[0]
df_clean['fiscal_year'] = df_clean['fiscal_year'].fillna(mode_year).astype(int)
print(f"3.5 fiscal_year recalculado desde award_date")

# 3.6 Eliminar filas con award_date nula (no imputables)
before = len(df_clean)
df_clean = df_clean.dropna(subset=['award_date'])
print(f"3.6 Filas eliminadas por award_date nula: {before - len(df_clean)}")

# ─────────────────────────────────────────────
# 4. COLUMNAS DERIVADAS
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("[4] COLUMNAS DERIVADAS")
print("=" * 60)

# Mes y trimestre
df_clean['month'] = df_clean['award_date'].dt.month
df_clean['quarter'] = df_clean['award_date'].dt.quarter
df_clean['month_year'] = df_clean['award_date'].dt.to_period('M').astype(str)

# Rango de gasto
def spend_range(amount):
    if amount < 1000:
        return "Micro (<1K)"
    elif amount < 10000:
        return "Small (1K-10K)"
    elif amount < 50000:
        return "Medium (10K-50K)"
    elif amount < 200000:
        return "Large (50K-200K)"
    else:
        return "Strategic (>200K)"

df_clean['spend_range'] = df_clean['award_amount'].apply(spend_range)

# Flag de alto valor (top 10% de contratos)
threshold_90 = df_clean['award_amount'].quantile(0.90)
df_clean['is_high_value'] = df_clean['award_amount'] >= threshold_90

print(f"\nColumnas derivadas creadas: month, quarter, month_year, spend_range, is_high_value")
print(f"Threshold alto valor (P90): ${threshold_90:,.2f}")

# ─────────────────────────────────────────────
# 5. VALIDACIÓN FINAL
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("[5] VALIDACIÓN FINAL")
print("=" * 60)

print(f"\nShape final: {df_clean.shape}")
print(f"Valores nulos restantes:\n{df_clean.isnull().sum()}")
print(f"\nDistribución spend_range:\n{df_clean['spend_range'].value_counts()}")
print(f"\nContratos alto valor: {df_clean['is_high_value'].sum()} ({df_clean['is_high_value'].mean()*100:.1f}%)")
print(f"\nGasto total: ${df_clean['award_amount'].sum():,.2f}")
print(f"Promedio por contrato: ${df_clean['award_amount'].mean():,.2f}")

# ─────────────────────────────────────────────
# 6. EXPORTAR DATASET LIMPIO
# ─────────────────────────────────────────────
df_clean.to_csv("../data/processed/latamcorp_procurement_clean.csv", index=False)
print(f"\n[6] Dataset limpio exportado a: data/processed/latamcorp_procurement_clean.csv")
print("\n✅ Fase 2 completada exitosamente.")
