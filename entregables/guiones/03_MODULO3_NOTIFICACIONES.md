# Guión de Presentación — Módulo 3: Notificaciones
## Marketplace USC · Desarrollado por Equipo 6

---

### ¿Qué hace este módulo?

Centraliza todos los avisos del Marketplace. Cuando ocurre cualquier evento de negocio (orden creada, pago aprobado, envío en tránsito, PQR), los otros módulos llaman a este servicio para que el usuario reciba la notificación en tiempo real en su panel.

**URL:** https://marketplace-usc-notificaciones.onrender.com
**Docs:** https://marketplace-usc-notificaciones.onrender.com/docs

---

### Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/notificaciones` | Crear una notificación para un usuario |
| `GET` | `/api/notificaciones/usuario/{id}` | Listar notificaciones de un usuario |
| `GET` | `/api/notificaciones/usuario/{id}/no-leidas/conteo` | Número de no leídas (badge) |
| `PUT` | `/api/notificaciones/{id}/leer` | Marcar una notificación como leída |
| `PUT` | `/api/notificaciones/usuario/{id}/leer-todas` | Marcar todas como leídas |
| `GET` | `/health` | Estado del servicio |

---

### Tipos de notificaciones soportados

| Tipo | Cuándo se genera |
|------|-----------------|
| `ORDEN_CREADA` | Al confirmar el carrito |
| `PAGO_APROBADO` | Cuando Equipo 2 confirma el pago |
| `PAGO_RECHAZADO` | Cuando el pago falla |
| `ENVIO_EN_TRANSITO` | Módulo 5 actualiza estado a EN_TRANSITO |
| `ENVIO_ENTREGADO` | Módulo 5 registra la entrega |
| `ESCROW_LIBERADO` | Módulo 6 libera fondos al vendedor |
| `INCIDENCIA_PQR` | Módulo 5 registra una queja o reclamo |
| `STOCK_BAJO` | Equipo 4 detecta stock crítico |
| `DEVOLUCION_SOLICITADA` | Cuando se solicita devolución |

---

### Cómo lo llaman los otros módulos

```
EQUIPO 2 (Pagos):
    POST /api/notificaciones
    { usuario_id, tipo: "PAGO_APROBADO", titulo, mensaje, referencia_id }

MÓDULO 5 (Seguimiento):
    POST /api/notificaciones
    { usuario_id, tipo: "ENVIO_EN_TRANSITO", ... }

MÓDULO 6 (Contabilidad):
    POST /api/notificaciones
    { usuario_id, tipo: "ESCROW_LIBERADO", ... }

FRONTEND (notifications.html):
    GET /api/notificaciones/usuario/{id}  → muestra el listado
    GET /api/notificaciones/usuario/{id}/no-leidas/conteo  → badge del header
```

---

### Base de datos

- **Supabase:** `xmrlazemifmepyahqsrz.supabase.co`
- **Tabla:** `notif_mensajes`
- **Campos clave:** `usuario_id`, `tipo`, `titulo`, `mensaje`, `leido`, `creado_en`
