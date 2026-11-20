# Guión de Presentación — Equipo 7: Catálogo
## Marketplace USC

---

### ¿Qué hace este módulo?

Mantiene el catálogo unificado de productos disponibles en el Marketplace. Sincroniza la información de productos desde el Equipo 4 (Inventario) y la expone al Frontend con un formato estandarizado.

**URL:** https://marketplace-usc-catalogo.onrender.com
**Docs:** https://marketplace-usc-catalogo.onrender.com/docs

---

### Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/catalogo` | Lista todos los productos del catálogo |
| `GET` | `/api/catalogo/{id}` | Detalle de un producto |
| `POST` | `/api/catalogo/sincronizar` | Sincronizar productos desde Equipo 4 |
| `GET` | `/` | Raíz del servicio |

---

### Cómo se interconecta con el resto

```
EQUIPO 4 (Inventario) — fuente de datos:
    → GET /api/productos   Obtiene productos para sincronizar

FRONTEND (catalog.html):
    → GET /api/catalogo    Muestra el listado de productos
    → GET /api/catalogo/{id}  Detalle de producto seleccionado
```

---

### Estrategia del Frontend para el catálogo

El frontend tiene un sistema de fallback por capas:

```
1. Intenta Equipo 4 (Inventario):
   GET https://marketplace-equipo4.onrender.com/api/productos ✅ Primario

2. Si falla, intenta Equipo 7 (Catálogo):
   GET https://marketplace-usc-catalogo.onrender.com/api/catalogo ⚡ Secundario

3. Si falla, usa Supabase directo:
   GET Supabase REST API → tabla productos 🔁 Respaldo
```

---

### URLs que necesita este módulo

```
URL_INVENTARIO = https://marketplace-equipo4.onrender.com
(Fuente de productos para sincronización)

CORS_ALLOWED_ORIGINS = https://marcketplace-usc.vercel.app,https://fgdiaz-jr.github.io
```

---

### Nota de integración

La ruta del catálogo es `/api/catalogo` (no `/api/productos`).
El frontend ya está configurado para consumir esta ruta correctamente.
