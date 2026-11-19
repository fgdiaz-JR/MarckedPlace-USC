# ENTREGABLE 1 — Contrato API v1 Acordado
## Proyecto: Marketplace USC | Repo Principal (Frontend)
**Equipo:** Grupo 3 & 6 (Frontend + Módulos Notificaciones y Contabilidad)
**Fecha:** 2026-11-13
**URL Repositorio:** https://github.com/fgdiaz-JR/MarckedPlace-USC

---

## Descripción del Componente

El **Frontend** es el cliente SPA (Single Page Application) que consume todos los microservicios. Actúa como **adaptador consumidor** de los 7 módulos y expone la interfaz de usuario final.

---

## Contrato de Integración: Frontend → Microservicios

### Protocolo y Formato
- **Protocolo:** HTTP/HTTPS REST
- **Formato de datos:** JSON (`Content-Type: application/json`)
- **Autenticación:** Bearer Token JWT emitido por Supabase Auth
- **CORS:** Todos los servicios permiten `*` en origen

### Punto de entrada centralizado: `frontend/js/config.js`

```javascript
const CONFIG = {
  supabase: {
    url: "https://xmrlazemifmepyahqsrz.supabase.co",
    publishableKey: "sb_publishable_BQpJ8OjTcJarh5ZIBW9mzw_OE3Ewyfk",
    jwksUrl: "https://xmrlazemifmepyahqsrz.supabase.co/auth/v1/.well-known/jwks.json"
  },
  services: {
    orders:        "http://localhost:8001/api",          // Equipo 1 (pendiente)
    payments:      "http://localhost:8002/api",          // Equipo 2 (pendiente)
    notifications: "https://marketplace-usc-notificaciones.onrender.com/api",  // LIVE
    inventory:     "http://localhost:8004/api",          // Equipo 4 (pendiente)
    tracking:      "https://marketplace-usc-seguimiento.onrender.com/api",     // LIVE
    accounting:    "https://marketplace-usc-contabilidad.onrender.com/api",    // LIVE
    catalog:       "http://localhost:8007/api"           // Equipo 7 (pendiente)
  }
};
```

### Cabeceras estándar de cada petición

```http
Authorization: Bearer <supabase_jwt_token>
Content-Type: application/json
Accept: application/json
```

---

## Endpoints consumidos por el Frontend (Módulos propios: 3, 5, 6)

### Módulo 3 — Notificaciones
| Verbo | Endpoint | Descripción |
|---|---|---|
| GET | `/api/notificaciones?usuario_id={id}` | Listar notificaciones del usuario |
| PUT | `/api/notificaciones/{id}/leer` | Marcar como leída |
| POST | `/api/notificaciones` | Crear notificación |

### Módulo 5 — Seguimiento
| Verbo | Endpoint | Descripción |
|---|---|---|
| GET | `/api/seguimiento/pedido/{pedido_id}` | Consultar estado de envío |
| GET | `/api/seguimiento?numero_guia={guia}` | Consultar por guía |
| POST | `/api/seguimiento/{guia}/pqr` | Reportar PQR |

### Módulo 6 — Contabilidad & Escrow
| Verbo | Endpoint | Descripción |
|---|---|---|
| GET | `/api/contabilidad/escrow/{pedido_id}` | Estado del escrow |
| GET | `/api/contabilidad/movimientos?pedido_id={id}` | Historial de movimientos |

---

## Contrato de Autenticación

```
Proveedor: Supabase Auth (xmrlazemifmepyahqsrz)
JWKS URL: https://xmrlazemifmepyahqsrz.supabase.co/auth/v1/.well-known/jwks.json
Algoritmo: RS256
Roles soportados: ADMIN | VENDEDOR | COMPRADOR
Campo de rol: user_metadata.role
```

**Usuarios de prueba acordados:**
| Email | Rol |
|---|---|
| admin@usc.edu.co | ADMIN |
| vendedor@usc.edu.co | VENDEDOR |
| comprador@usc.edu.co | COMPRADOR |

---

## Reglas de Negocio Fijas (acordadas con la cátedra)

| Regla | Valor |
|---|---|
| IVA | 19% |
| Envío gratis desde | $200.000 COP |
| Costo de envío estándar | $15.000 COP |
| Comisión de plataforma | 5% |
| Liberación automática del Escrow | 72 horas tras entrega |

