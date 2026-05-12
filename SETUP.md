# Guía de publicación en GitHub

## Paso 1 — Crear el repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre: `procurement-spend-analytics`
3. Descripción: `End-to-end procurement spend analysis: Python + SQL + interactive dashboard | FY2022-23 | $205M analyzed`
4. Visibilidad: **Public** (necesario para GitHub Pages gratis)
5. **No** inicialices con README (ya tienes uno)
6. Click en **Create repository**

---

## Paso 2 — Subir el proyecto

Desde la carpeta del proyecto en tu terminal:

```bash
cd procurement-spend-analytics

git init
git add .
git commit -m "Initial commit: procurement spend analytics FY2022-23"

git branch -M main
git remote add origin https://github.com/TU-USUARIO/procurement-spend-analytics.git
git push -u origin main
```

Reemplaza `TU-USUARIO` con tu nombre de usuario de GitHub.

---

## Paso 3 — Activar GitHub Pages (para el dashboard)

1. En tu repo, ve a **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` · Folder: `/dashboard`
4. Click **Save**
5. Espera ~2 minutos
6. Tu dashboard estará en: `https://TU-USUARIO.github.io/procurement-spend-analytics`

---

## Paso 4 — Actualizar links en README

Abre `README.md` y reemplaza:
- `tu-usuario` → tu usuario real de GitHub
- `tu-perfil` en el link de LinkedIn → tu perfil real

```bash
git add README.md
git commit -m "Update links with real GitHub and LinkedIn URLs"
git push
```

---

## Paso 5 — Verificar que todo se ve bien

Checklist antes de compartir:

- [ ] README se renderiza correctamente en GitHub (headers, tablas, badges)
- [ ] Dashboard carga en la URL de GitHub Pages
- [ ] Los 3 scripts Python corren sin errores desde cero (`pip install -r requirements.txt`)
- [ ] `sql/queries.sql` se puede abrir y leer fácilmente
- [ ] Carpeta `article/` tiene el artículo listo

---

## Paso 6 — Compartir en LinkedIn

Texto sugerido para el post de anuncio:

```
Acabo de publicar mi primer proyecto de portfolio de data analytics.

Analicé $205M en contratos de procurement usando Python, SQL y un 
dashboard interactivo — y encontré que 5 vendors concentran el 83% 
del gasto. Eso no es eficiencia, es riesgo.

El proyecto completo (código + dashboard + caso de estudio) está en GitHub.

[link al repo] [link al dashboard]

#DataAnalytics #Procurement #Python #SQL #SupplyChain #Panama
```

---

## Tips para el README en GitHub

- Los badges se renderizan automáticamente ✓
- Las tablas se ven limpias en GitHub Markdown ✓
- Los bloques de código tienen syntax highlighting ✓
- La estructura de árbol en los code blocks se ve excelente ✓
