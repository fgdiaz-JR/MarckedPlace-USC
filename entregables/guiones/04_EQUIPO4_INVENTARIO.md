# Guión de Presentación — Equipo 4: Inventario y Carrito
## Marketplace USC

---

### ¿Qué hace este módulo?

Gestiona el stock de productos, el carrito de compras y la reserva de inventario durante el proceso de pago. Es la fuente principal de productos para el catálogo del frontend.

**URL:** https://marketplace-equipo4.onrender.com
**Docs:** https://marketplace-equipo4.onrender.com/docs

---

### Funcionalidades implementadas

- **Catálogo de productos:** CRUD completo con imágenes
- **Control de inventario:** stock disponible, alertas de stock bajo
- **Reserva de stock:** bloquea unidades durante el checkout para evitar sobreventas
- **Confirmación:** confirma la reserva cuando el pago es aprobado
- **Liberación:** *(en implementación)* revierte la reserva si el pago falla
- **Carrito:** gestión de ítems con validación de stock en tiempo real
- **Movimientos:** historial de entradas y salidas de inventario

---

### Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/productos` | Lista todos los productos |
| `GET` | `/api/productos/{id}` | Producto específico |
| `POST` | `/api/inventario/reservar` | Reservar stock (antes del pago) |
| `POST` | `/api/inventario/confirmar/{ref}` | Confirmar reserva (pago aprobado) |
| `POST` | `/api/inventario/liberar/{ref}` | Liberar reserva (pago fallido) *(en implementación)* |
| `GET` | `/api/inventario/stock-bajo` | Productos con stock crítico |
| `GET/POST` | `/api/carrito` | Gestión del carrito |

---

### Cómo se interconecta con el resto

```
FRONTEND (catalog.html):
    → GET /api/productos      Muestra el catálogo de productos

EQUIPO 1 (Órdenes):
    → Verifica stock disponible antes de confirmar la orden

EQUIPO 2 (Pagos):
    → POST /api/inventario/reservar      Bloquea stock al iniciar el pago
    → POST /api/inventario/confirmar/{ref}  Confirma al pagar con éxito
    → POST /api/inventario/liberar/{ref}    Revierte si el pago falla

MÓDULO 3 (Notificaciones):
    → POST /api/notificaciones  Cuando stock llega a nivel crítico
```

---

### Flujo de reserva de inventario

```
Comprador inicia pago
      ↓
POST /api/inventario/reservar
{ referencia_id: "uuid-orden", items: [{producto_id, cantidad}] }
      ↓
Stock bloqueado temporalmente
      ↓
  ✅ Pago aprobado → POST /api/inventario/confirmar/{referencia_id}
  ❌ Pago fallido  → POST /api/inventario/liberar/{referencia_id}
```

---

### Body de reserva

```json
{
  "referencia_id": "uuid-de-la-orden",
  "items": [
    { "producto_id": "uuid-producto", "cantidad": 2 }
  ]
}
```
