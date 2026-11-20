# Guión de Presentación — Módulo 6: Contabilidad y Escrow
## Marketplace USC · Desarrollado por Equipo 6

---

### ¿Qué hace este módulo?

Gestiona la tesorería del Marketplace. Cuando un comprador paga, el dinero no va directamente al vendedor: queda retenido en custodia (Escrow) por 72 horas. Esto protege al comprador en caso de problemas con el pedido. También calcula y registra la comisión del 5% que cobra la plataforma.

**URL:** https://marketplace-usc-contabilidad.onrender.com
**Docs:** https://marketplace-usc-contabilidad.onrender.com/docs

---

### Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/contabilidad/escrow/retener` | Crear retención Escrow al pagar |
| `POST` | `/api/contabilidad/escrow/marcar-entrega/{id}` | Inicia conteo 72h (llamado por M5) |
| `POST` | `/api/contabilidad/escrow/liberar/{id}` | Liberar fondos al vendedor |
| `POST` | `/api/contabilidad/escrow/bloquear/{id}` | Congelar por disputa PQR |
| `GET` | `/api/contabilidad/resumen-general` | Panel ADMIN (requiere rol ADMIN) |
| `GET` | `/api/contabilidad/vendedor/{id}` | Balance de un vendedor |
| `GET` | `/health` | Estado del servicio |

---

### Reglas de negocio implementadas

| Regla | Valor |
|-------|-------|
| Comisión plataforma | **5% sobre subtotal de productos** (sin envío ni IVA) |
| Retención Escrow | Mínimo **72 horas** tras confirmar la entrega |
| Liberación automática | Al expirar las 72h o por conformidad del comprador |
| Bloqueo por PQR | Congela indefinidamente hasta resolución manual |
| Idempotencia | No duplica registros si el mismo `pedido_id` llega dos veces |

---

### Ejemplo de cálculo

```
Pedido: $200.000 (subtotal) + $15.000 (envío) = $215.000 total

Comisión: $200.000 × 5% = $10.000  ← solo sobre subtotal
Neto vendedor: $215.000 - $10.000 = $205.000

Escrow retiene: $215.000 durante 72h
Después de 72h: vende $205.000 al vendedor + $10.000 queda en plataforma
```

---

### Cómo se interconecta con el resto

```
EQUIPO 2 (Pagos):
    → POST /api/contabilidad/escrow/retener   Crea la retención al confirmar el pago
    → POST /api/contabilidad/escrow/liberar   Libera fondos (pago digital aprobado)
    → POST /api/contabilidad/escrow/bloquear  Bloquea si hay disputa

MÓDULO 5 (Seguimiento):
    → POST /api/contabilidad/escrow/marcar-entrega/{id}  Al registrar entrega física
    → POST /api/contabilidad/escrow/bloquear/{id}         Al registrar PQR

FRONTEND (admin-accounting.html):
    → GET  /api/contabilidad/resumen-general  Panel ADMIN con totales
    → GET  /api/contabilidad/vendedor/{id}    Balance por vendedor
```

---

### Ciclo de vida del Escrow

```
PAGO CONFIRMADO
      ↓
   RETENIDO  ←──── estado inicial (fondos en custodia)
      ↓
  Entrega confirmada (M5 llama a marcar-entrega)
      ↓
  Espera 72 horas
      ↓
   LIBERADO  ───→ Fondos disponibles para el vendedor
      ↓
  (Si hay PQR antes de las 72h)
      ↓
  BLOQUEADO_PQR  ───→ Admin resuelve manualmente
      ↓
   REEMBOLSADO  ───→ Devuelto al comprador
```

---

### Base de datos

- **Supabase:** `xmrlazemifmepyahqsrz.supabase.co`
- **Tablas:** `cont_escrow`, `cont_movimientos`, `cont_cuentas`
- **Seguridad:** `/resumen-general` requiere `app_metadata.role = ADMIN` en el JWT
