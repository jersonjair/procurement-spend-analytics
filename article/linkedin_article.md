# Cómo usé Python, SQL y un dashboard interactivo para analizar $205M en contratos de procurement

**Por Jerson · Procurement Data Analyst · Mayo 2025**

---

Hace unas semanas me hice una pregunta que todo analista de procurement debería hacerse antes de tomar cualquier decisión de compra:

> *¿Realmente sabemos dónde está yendo el dinero?*

La respuesta honesta, en la mayoría de organizaciones, es: **no del todo**.

Los datos existen. Están en el ERP, en los contratos, en los correos. Pero dispersos, sin estructura, sin historia. Este proyecto nació de querer responder esa pregunta correctamente — con datos, con código, y con un dashboard que cualquier gerente pueda usar.

---

## El problema de negocio

Imagina una empresa de distribución regional — llamémosla **LatamCorp S.A.** — con operaciones en Panamá y relaciones comerciales con 20 proveedores activos. La gerencia tiene tres sospechas:

1. El gasto está **concentrado en pocos vendors** — lo cual es un riesgo operacional.
2. Algunas **categorías están creciendo sin control** — nadie sabe por qué.
3. No hay **visibilidad del gasto por período** — se toman decisiones a ciegas.

Mi tarea: construir un análisis completo que responda estas tres preguntas con datos reales.

---

## El stack técnico

Mantuve todo simple e intencional. No usé nada que no pueda justificar:

- **Python + pandas** — limpieza, transformación, EDA y generación de gráficos
- **SQL con DuckDB** — consultas analíticas directamente sobre el CSV procesado
- **HTML + Chart.js** — dashboard interactivo standalone, sin servidor, sin Power BI license

El dataset: **4,930 contratos de compra**, FY2022–2023, $205M en gasto total.

---

## Lo que encontré

### 1. El problema Pareto: 5 vendors, 83% del gasto

Este fue el hallazgo más crítico.

De 20 proveedores activos, **solo 5 concentran el 83% del gasto total**:

| Vendor | Gasto Total | % del Total |
|--------|-------------|-------------|
| Distribuidora Global S.A. | $45.9M | 22.4% |
| TechSupplies Panama | $38.9M | 18.9% |
| Grupo Logístico del Istmo | $30.7M | 15.0% |
| Oficentro Internacional | $29.9M | 14.6% |
| Ferremax Industrial | $25.0M | 12.2% |

Esto no es eficiencia — es fragilidad. Un problema con cualquiera de estos vendors (quiebra, desabasto, renegociación de precios) impactaría materialmente la operación.

**¿Qué hacer?** Implementar una política de tope del 15% por vendor y desarrollar proveedores alternativos en las categorías de mayor concentración.

---

### 2. El índice HHI: en el límite de la zona de riesgo

Para medir concentración objetivamente, calculé el **Índice Herfindahl-Hirschman (HHI)** — la misma métrica que usan los reguladores antimonopolio.

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

**HHI = 1,466** — está dentro del umbral "competitivo" (< 1,500), pero a solo 34 puntos del límite. Un contrato adicional importante con Distribuidora Global lo empujaría a zona moderada.

Este número debería estar en el dashboard de cualquier director de procurement.

---

### 3. IT creció 23% interanual. Logistics creció 53%. ¿Por qué?

El análisis año contra año reveló dos patrones muy distintos:

**Categorías en crecimiento:**
- Logistics & Transport: **+53%** ($12.6M → $19.3M)
- Medical Supplies: **+27%**
- IT & Technology: **+23%** ($22M → $27.1M)

**Categorías en contracción:**
- Professional Services: **-17%** ($15.1M → $12.6M)
- Maintenance & Repair: **-11%**

El crecimiento de IT es esperado y positivo — correlaciona con iniciativas de digitalización. Pero el salto de **53% en Logistics** en un solo año merece una revisión: ¿es expansión real del negocio o ineficiencia en la cadena de distribución?

La caída en Professional Services puede ser una señal positiva de capacidad interna creciente — o puede indicar recortes presupuestarios que afectan proyectos estratégicos.

**Sin datos, ambas son solo opiniones.**

---

### 4. Diciembre 2023: el pico anómalo

La tendencia mensual mostró algo que no esperaba: un pico de **$12.5M en diciembre 2023** — el más alto de todo el período analizado, 50% por encima del mes anterior.

Este tipo de concentración al cierre del año fiscal es un patrón clásico de *"gasta o pierde el presupuesto"* — una práctica que infla costos, precipita contratos mal negociados y crea riesgo operacional.

**Recomendación:** revisar los contratos de alto valor adjudicados en noviembre–diciembre y evaluar si el proceso de planificación presupuestaria permite mayor distribución durante el año.

---

## La parte técnica que más me gustó: SQL con window functions

Una de las partes más satisfactorias del proyecto fue escribir las queries analíticas. Aquí la que calcula el acumulado Pareto directamente en SQL:

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

No necesité Python para esto. SQL puro, con una window function anidada, calcula el porcentaje acumulado en una sola pasada. Limpio y reproducible.

---

## Qué aprendí construyendo esto

**Sobre datos:** Los datos sucios son la norma, no la excepción. El dataset tenía 30 duplicados exactos, 158 nulos en montos, y 38 vendors únicos que después de estandarizar casing se redujeron a 20. La limpieza tomó tanto tiempo como el análisis.

**Sobre negocio:** Los números son el punto de partida, no el destino. El HHI de 1,466 es interesante. La pregunta *"¿qué hacemos con eso?"* es donde está el valor real.

**Sobre comunicación:** Un dashboard que nadie entiende es tan inútil como no tener datos. Diseñé el dashboard para que un gerente sin contexto técnico pudiera leerlo en 2 minutos y extraer decisiones concretas.

---

## Recursos y código

Todo el código está disponible en GitHub — incluyendo el script de limpieza, las 10 queries SQL documentadas, los scripts de EDA con 6 visualizaciones, y el dashboard HTML interactivo:

🔗 **GitHub:** `github.com/tu-usuario/procurement-spend-analytics`
🔗 **Dashboard:** `tu-usuario.github.io/procurement-spend-analytics`

Si estás trabajando en procurement, supply chain o análisis de datos y quieres discutir la metodología — me encuentras en LinkedIn.

---

*Este análisis usa datos sintéticos generados para propósitos de portfolio. La metodología es aplicable a datasets reales de PanamaCompra, USAspending.gov, o sistemas ERP internos.*

---

**Tags:** #DataAnalytics #Procurement #Python #SQL #SupplyChain #PowerBI #DataScience #Panama
