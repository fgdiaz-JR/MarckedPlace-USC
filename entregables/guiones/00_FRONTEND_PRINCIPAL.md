# Guión de Presentación — Frontend Principal
## Marketplace USC · Equipo 6 (Frontend + M3 + M5 + M6)

---

### ¿Qué es el Frontend?

El Frontend es la capa visual del Marketplace USC. Es la única parte que el usuario final ve y toca. Está construido en HTML, CSS y JavaScript puro (sin frameworks), desplegado en **Vercel** y **GitHub Pages**.

**URL de producción:** https://marcketplace-usc.vercel.app

---

### ¿Qué hace?

Actúa como el **orquestador principal**: conecta a los 7 microservicios de los equipos en un solo flujo de compra coherente. Ningún equipo se llama entre sí directamente desde el navegador — todo pasa por el frontend.

---

### Páginas y qué módulo usa cada una

| Página | Función | Módulo que consume |
|--------|---------|-------------------|
| `login.html` | Autenticación con JWT | Supabase Auth |
| `catalog.html` | Ver productos disponibles | Eq4 Inventario → Eq7 Catálogo → Supabase |
| `cart.html` | Carrito de compras | Local (CartStore) |
| `checkout.html` | Finalizar compra y pagar | Eq1 Órdenes · Eq2 Pagos · M6 Contabilidad · M5 Seguimiento · M3 Notificaciones |
| `orders.html` | Historial de pedidos | Eq1 Órdenes (Supabase `ord_pedidos`) |
| `tracking.html` | Seguimiento del envío | M5 Seguimiento |
| `notifications.html` | Centro de notificaciones | M3 Notificaciones |
| `admin-accounting.html` | Panel financiero ADMIN | M6 Contabilidad |
| `seller-dashboard.html` | Panel del vendedor | Eq4 Inventario · M6 Contabilidad |

---

### Flujo completo de una compra (lo que ocurre al hacer clic en "Pagar")

```
1. COMPRADOR selecciona productos → catalog.html (Eq4/Eq7)
         ↓
2. Agrega al carrito → cart.html (localStorage)
         ↓
3. Va al checkout → checkout.html
         ↓
4. Elige dirección y método de pago (PSE / QR / Contra Entrega)
         ↓
5. Clic en "Pagar y Generar Pedido":
   ├── Crea orden          → Supabase ord_pedidos       (Eq1)
   ├── Registra pago       → Supabase pag_transacciones (Eq2)
   ├── Crea retención      → M6 Contabilidad Escrow
   ├── Crea seguimiento    → M5 Seguimiento
   └── Envía notificación  → M3 Notificaciones
         ↓
6. Redirige a orders.html con confirmación
```

---

### Arquitectura de configuración (`config.js`)

Todas las URLs de los 7 equipos están centralizadas en un solo archivo:

```javascript
const CONFIG = {
  services: {
    orders:        "https://ordenes-thaliana.onrender.com/api",
    payments:      "https://marketplace-usc-pagos-staging.onrender.com/api",
    notifications: "https://marketplace-usc-notificaciones.onrender.com/api",
    inventory:     "https://marketplace-equipo4.onrender.com/api",
    tracking:      "https://marketplace-usc-seguimiento.onrender.com/api",
    accounting:    "https://marketplace-usc-contabilidad.onrender.com/api",
    catalog:       "https://marketplace-usc-catalogo.onrender.com/api"
  }
}
```

Cambiar una URL en este archivo actualiza toda la plataforma.

---

### Seguridad JWT

- El token de Supabase se valida en cada backend mediante JWKS
- El rol del usuario se lee de `app_metadata.role` (ADMIN / VENDEDOR / COMPRADOR)
- El panel `/admin-accounting` solo es visible para rol ADMIN

---

### Reglas de negocio implementadas

| Regla | Valor |
|-------|-------|
| Comisión plataforma | 5% sobre subtotal de productos |
| IVA | 19% |
| Envío gratis | Pedidos ≥ $200.000 COP |
| Envío estándar | $15.000 COP |
| Escrow | Retención 72h tras entrega |
| COD anticipo | $50.000 COP fijo |
