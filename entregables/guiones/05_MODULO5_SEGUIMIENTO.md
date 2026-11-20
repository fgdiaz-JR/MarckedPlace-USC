# Guión de Presentación — Módulo 5: Seguimiento de Entregas
## Marketplace USC · Desarrollado por Equipo 6

---

### ¿Qué hace este módulo?

Rastrea el recorrido físico de cada pedido desde que sale del vendedor hasta que llega al comprador. Genera números de guía automáticos, registra evidencias de entrega y coordina con Contabilidad para liberar los fondos Escrow al confirmar la entrega.

**URL:** https://marketplace-usc-seguimiento.onrender.com
**Docs:** https://marketplace-usc-seguimiento.onrender.com/docs

---

### Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/seguimiento/crear` | Crear seguimiento para un pedido |
| `GET` | `/api/seguimiento/pedido/{id}` | Consultar por pedido |
| `GET` | `/api/seguimiento?numero_guia=X` | Consultar por número de guía |
| `GET` | `/api/seguimiento/comprador/{id}` | Todos los envíos de un comprador |
| `GET` | `/api/seguimiento/vendedor/{id}` | Todos los envíos de un vendedor |
| `PUT` | `/api/seguimiento/{guia}/estado` | Actualizar estado del envío |
| `POST` | `/api/seguimiento/{guia}/entregar` | Registrar entrega con evidencia |
| `POST` | `/api/seguimiento/{guia}/pqr` | Registrar PQR (queja o reclamo) |
| `GET` | `/health` | Estado del servicio |

---

### Estados del ciclo de vida de un envío

```
PENDIENTE → PENDIENTE_DESPACHO → RECOGIDO → EN_TRANSITO → EN_DESTINO → ENTREGADO
                                                                             ↓
                                                                        DEVOLUCION
                                                     FALLIDO ←──────────────┘
```

> `PENDIENTE_DESPACHO`: estado exclusivo para pagos Contra Entrega (COD)

---

### Automatizaciones internas

| Evento | Acción automática |
|--------|-----------------|
| Estado → `EN_TRANSITO` | Notifica al comprador vía M3 |
| Estado → `EN_DESTINO` | Notifica al comprador vía M3 |
| `POST /entregar` | Notifica entrega + inicia conteo 72h en M6 Escrow |
| `POST /pqr` PERDIDA/DAÑO | Congela Escrow en M6 + notifica comprador y vendedor |

---

### Cómo se interconecta con el resto

```
EQUIPO 2 (Pagos):
    → POST /api/seguimiento/crear     Crea el seguimiento al confirmar el pago
    → PUT  /api/seguimiento/{guia}/estado  Actualiza a PENDIENTE_DESPACHO (COD)

FRONTEND (tracking.html):
    → GET  /api/seguimiento/pedido/{id}   Muestra el estado al comprador

MÓDULO 3 (Notificaciones):
    ← M5 llama a M3 automáticamente en EN_TRANSITO, EN_DESTINO y ENTREGADO

MÓDULO 6 (Contabilidad):
    ← M5 llama a M6 al registrar entrega → inicia 72h para liberar Escrow
    ← M5 llama a M6 al registrar PQR → congela el Escrow
```

---

### Base de datos

- **Supabase:** `zludypuqnnamouhmjfuu.supabase.co`
- **Tablas:** `ent_seguimientos`, `ent_evidencias`
- **Campos clave:** `pedido_id`, `numero_guia`, `estado`, `transportadora`, `fecha_entrega_real`
