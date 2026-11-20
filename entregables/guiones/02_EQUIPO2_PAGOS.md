# Guión de Presentación — Equipo 2: Pasarela de Pagos
## Marketplace USC

---

### ¿Qué hace este módulo?

Orquesta el proceso de pago completo. Es el módulo más crítico del flujo transaccional: recibe el pago del comprador y coordina con Inventario, Contabilidad, Seguimiento y Notificaciones para cerrar la compra de forma atómica.

**URL:** https://marketplace-usc-pagos-staging.onrender.com
**Docs:** https://marketplace-usc-pagos-staging.onrender.com/docs

---

### Métodos de pago soportados

| Método | Flujo |
|--------|-------|
| **PSE** | Pago online directo — aprobado → libera todo |
| **QR** | Código QR de pago — aprobado → libera todo |
| **COD (Contra Entrega)** | Anticipo $50.000 → confirma inventario → libera Escrow al entregar |

---

### Cómo se interconecta con el resto

```
FRONTEND
    → POST /api/pagos/procesar     Inicia el proceso de pago

EQUIPO 1 (Órdenes) — Equipo 2 llama a Equipo 1:
    → GET  /api/ordenes/{id}       Verificar que la orden existe
    → PUT  /api/ordenes/{id}/estado  Actualizar estado (PAGADO / CANCELADO)

EQUIPO 4 (Inventario) — Equipo 2 llama a Equipo 4:
    → POST /api/inventario/confirmar/{ref}  Confirmar reserva de stock
    → POST /api/inventario/liberar/{ref}    Revertir reserva si falla el pago

MÓDULO 6 (Contabilidad) — Equipo 2 llama a M6:
    → POST /api/contabilidad/escrow/retener     Crear retención Escrow
    → POST /api/contabilidad/escrow/liberar     Liberar fondos al vendedor
    → POST /api/contabilidad/escrow/bloquear    Bloquear por disputa

MÓDULO 5 (Seguimiento) — Equipo 2 llama a M5:
    → PUT  /api/seguimiento/{id}/estado     Estado: PENDIENTE_DESPACHO o ENTREGADO

MÓDULO 3 (Notificaciones) — Equipo 2 llama a M3:
    → POST /api/notificaciones     Avisar al comprador y vendedor
```

---

### Flujo de pago exitoso (PSE / QR)

```
1. Frontend envía datos de pago a Equipo 2
2. Equipo 2 verifica la orden en Equipo 1
3. Equipo 2 crea retención Escrow en M6
4. Equipo 2 procesa el pago con la pasarela
5. ✅ APROBADO:
   - Confirma inventario en Equipo 4
   - Libera Escrow en M6
   - Marca orden como PAGADO en Equipo 1
   - Actualiza seguimiento en M5
   - Notifica al comprador y vendedor vía M3
```

---

### Flujo COD (Contra Entrega)

```
1. Comprador paga anticipo de $50.000
2. Equipo 2 confirma inventario en Equipo 4
3. Orden pasa a estado EN_PREPARACION (no PAGADO)
4. Escrow creado pero NO liberado (espera entrega)
5. Al entregar → Seguimiento notifica a M6 → libera Escrow
```

---

### Flujo de pago fallido

```
❌ RECHAZADO:
   - Libera reserva de inventario en Equipo 4
   - Bloquea o cancela Escrow en M6
   - Marca orden como CANCELADA en Equipo 1
   - Notifica al comprador vía M3
```

---

### URLs que necesita este módulo

```
SUPABASE_URL       = https://xmrlazemifmepyahqsrz.supabase.co
URL_ORDENES        = https://ordenes-thaliana.onrender.com
URL_INVENTARIO     = https://marketplace-equipo4.onrender.com
URL_CONTABILIDAD   = https://marketplace-usc-contabilidad.onrender.com
URL_SEGUIMIENTO    = https://marketplace-usc-seguimiento.onrender.com
URL_NOTIFICACIONES = https://marketplace-usc-notificaciones.onrender.com
CORS_ALLOWED_ORIGINS = https://marcketplace-usc.vercel.app,https://fgdiaz-jr.github.io
```
