# Guión de Presentación — Equipo 1: Órdenes y Envíos
## Marketplace USC

---

### ¿Qué hace este módulo?

Gestiona el ciclo de vida completo de un pedido: desde su creación hasta su entrega. También administra las direcciones del comprador, calcula tarifas de envío y genera números de guía.

**URL:** https://ordenes-thaliana.onrender.com
**Docs:** https://ordenes-thaliana.onrender.com/docs

---

### Funcionalidades implementadas

- **Catálogo DIVIPOLA:** municipios y departamentos oficiales de Colombia
- **Zonas de cobertura:** activación/desactivación por zona
- **Opciones de envío:** creación y gestión de transportadoras
- **Tarifas por peso:** rangos configurables sin superposición
- **Cotización previa:** calcula el costo antes de crear la orden
- **Órdenes:** creación, consulta y actualización de estado
- **Direcciones del comprador:** alta, edición, eliminación y dirección predeterminada

---

### Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/envios/cotizaciones` | Calcula costo de envío antes de pagar |
| `GET/POST` | `/api/ordenes` | Lista o crea una orden |
| `GET` | `/api/ordenes/{id}` | Consulta una orden específica |
| `PUT` | `/api/ordenes/{id}/estado` | Actualiza el estado de la orden |
| `GET` | `/api/ordenes/{id}/rastreo` | Número de guía y trazabilidad |
| `GET/POST` | `/api/direcciones` | Direcciones del comprador |
| `GET` | `/api/envios/municipios` | Lista de municipios DIVIPOLA |
| `GET` | `/api/health` | Estado del servicio |

---

### Cómo se interconecta con el resto

```
FRONTEND (checkout.html)
    → POST /api/ordenes           Crear orden con ítems y dirección
    → POST /api/envios/cotizaciones  Calcular costo de envío

EQUIPO 2 (Pagos)
    → GET  /api/ordenes/{id}      Verificar que la orden existe antes de cobrar
    → PUT  /api/ordenes/{id}/estado  Marcar como PAGADO o CANCELADO

MÓDULO 5 (Seguimiento)
    ← Recibe pedido_id para crear el seguimiento de entrega

EQUIPO 4 (Inventario)
    → Verifica stock disponible antes de confirmar la orden
```

---

### URLs que necesita este módulo

```
SUPABASE_URL       = https://xmrlazemifmepyahqsrz.supabase.co
URL_INVENTARIO     = https://marketplace-equipo4.onrender.com
URL_CONTABILIDAD   = https://marketplace-usc-contabilidad.onrender.com
URL_SEGUIMIENTO    = https://marketplace-usc-seguimiento.onrender.com
URL_NOTIFICACIONES = https://marketplace-usc-notificaciones.onrender.com
URL_CATALOGO       = https://marketplace-usc-catalogo.onrender.com
```

---

### Estados de una orden

```
PENDIENTE_PAGO → CONFIRMADA → EN_PREPARACION → ENVIADA → ENTREGADA
                     ↓
                 CANCELADA
```
