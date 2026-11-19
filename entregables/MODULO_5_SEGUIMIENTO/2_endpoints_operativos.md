# ENTREGABLE 2 — Endpoints Operativos REALES
## Proyecto: Marketplace USC | Modulo 5 — Seguimiento de Entregas
**Fecha:** 2026-11-13

---

## Estado: OPERATIVO EN PRODUCCION (REAL, no MOCK)

### Informacion del Servicio

| Dato | Valor |
|---|---|
| URL Base | https://marketplace-usc-seguimiento.onrender.com |
| Plataforma | Render (Free Tier) |
| Runtime | Python 3.11 / FastAPI 0.111 |
| Documentacion | https://marketplace-usc-seguimiento.onrender.com/docs |
| ReDoc | https://marketplace-usc-seguimiento.onrender.com/redoc |
| Render Service ID | srv-dbrqdddg1s2s73d93gvg |
| Supabase URL | https://zludypuqnnamouhmjfuu.supabase.co |

---

## Verificacion de Endpoints en Produccion

### GET /health
```
URL: https://marketplace-usc-seguimiento.onrender.com/health
Metodo: GET
Autenticacion: No requerida
```

```bash
curl -X GET https://marketplace-usc-seguimiento.onrender.com/health
```

**Respuesta verificada (HTTP 200):**
```json
{
  "status": "healthy",
  "service": "seguimiento_entregas",
  "team": "Equipo 5",
  "version": "1.0.0",
  "supabase_connected": true
}
```

---

### POST /api/seguimiento/crear
```
URL: https://marketplace-usc-seguimiento.onrender.com/api/seguimiento/crear
Metodo: POST
Content-Type: application/json
```

```bash
curl -X POST https://marketplace-usc-seguimiento.onrender.com/api/seguimiento/crear \
  -H "Content-Type: application/json" \
  -d '{
    "pedido_id": "00000000-0000-0000-0000-000000000001",
    "vendedor_id": "00000000-0000-0000-0000-000000000002",
    "comprador_id": "00000000-0000-0000-0000-000000000003",
    "origen": "Cali",
    "destino": "Bogota",
    "direccion_entrega": "Calle 100 # 15-20, Bogota"
  }'
```

---

### GET /api/seguimiento/pedido/{pedido_id}
```
URL: https://marketplace-usc-seguimiento.onrender.com/api/seguimiento/pedido/{pedido_id}
Metodo: GET
```

---

### GET /api/seguimiento?numero_guia={guia}
```
URL: https://marketplace-usc-seguimiento.onrender.com/api/seguimiento?numero_guia=USC-XXXXXXXX
Metodo: GET
```

---

### PUT /api/seguimiento/{numero_guia}/estado
```
URL: https://marketplace-usc-seguimiento.onrender.com/api/seguimiento/{guia}/estado
Metodo: PUT
Content-Type: application/json
```

---

### POST /api/seguimiento/{numero_guia}/entregar
```
URL: https://marketplace-usc-seguimiento.onrender.com/api/seguimiento/{guia}/entregar
Metodo: POST
```

---

### POST /api/seguimiento/{numero_guia}/pqr
```
URL: https://marketplace-usc-seguimiento.onrender.com/api/seguimiento/{guia}/pqr
Metodo: POST
```

---

## Variables de Entorno en Produccion (Render)

| Variable | Valor |
|---|---|
| SUPABASE_URL | https://zludypuqnnamouhmjfuu.supabase.co |
| SUPABASE_KEY | [service_role JWT — configurado en Render] |
| URL_CONTABILIDAD | https://marketplace-usc-contabilidad.onrender.com/api |
| URL_NOTIFICACIONES | https://marketplace-usc-notificaciones.onrender.com/api |
| PYTHON_VERSION | 3.11.0 |

