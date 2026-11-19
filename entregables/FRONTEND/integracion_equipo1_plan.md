# Plan de Integración — Equipo 1 (Envíos y Logística)
## Proyecto: Marketplace USC | Frontend Principal
**Fecha:** 2026-11-19

---

## Qué construyó el Equipo 1

| Funcionalidad | Endpoints |
|---|---|
| Cobertura municipal DIVIPOLA | `GET /api/envios/municipios` |
| Departamentos | `GET /api/envios/departamentos` |
| Zonas por departamento | `GET /api/envios/zonas` |
| Opciones de envío activas | `GET /api/envios/opciones` |
| Cotización previa (cálculo tarifa) | `POST /api/envios/cotizar` |
| Transportadoras activas | `GET /api/envios/transportadoras` |
| Direcciones del comprador | `GET/POST/PUT/DELETE /api/direcciones` |
| Peso/dimensiones de producto | `GET/PUT /api/productos/{id}/envio` |
| Tarifa por zona, opción y peso | `GET /api/envios/tarifas` |

---

## Cambios requeridos en el Frontend

### 1. `frontend/js/config.js`
Cambiar `orders: "http://localhost:8001/api"` por la URL real de Render del Equipo 1.

```javascript
orders: "https://<URL-EQUIPO-1>.onrender.com/api"
```

### 2. `frontend/checkout.html` — 4 bloques nuevos

**Bloque A — Selector de dirección guardada:**
```html
<div class="field">
  <label>Dirección de entrega</label>
  <select id="savedAddressSelect">
    <option value="">Cargando direcciones...</option>
  </select>
  <button id="addNewAddressBtn" class="btn btn-soft">+ Nueva dirección</button>
</div>
```

**Bloque B — Selector de municipio (DIVIPOLA):**
```html
<select id="departamentoSelect">...</select>
<select id="municipioSelect">...</select>
```

**Bloque C — Cotización de envío:**
```html
<div id="shippingQuotePanel">
  <button id="calcShippingBtn" class="btn btn-soft">Calcular envío</button>
  <div id="shippingOptions"></div>  <!-- Lista de opciones con tarifas -->
</div>
```

**Bloque D — Resumen actualizado:**
```html
<strong id="chkShipping">Calculando...</strong>
<!-- Ya existe, solo se actualiza con el valor de la cotización -->
```

### 3. `frontend/js/checkout.js` (nuevo módulo)

Lógica que se debe agregar:

```javascript
// Al cargar la página
async function initShipping() {
  // 1. Cargar direcciones guardadas del comprador
  const dirs = await fetch(`${CONFIG.services.orders}/direcciones?comprador_id=${user.id}`);
  
  // 2. Cargar departamentos DIVIPOLA
  const deps = await fetch(`${CONFIG.services.orders}/envios/departamentos`);
  
  // 3. Al seleccionar municipio → cotizar
  async function cotizarEnvio(municipio_id, peso_total) {
    const quote = await fetch(`${CONFIG.services.orders}/envios/cotizar`, {
      method: "POST",
      body: JSON.stringify({
        municipio_destino_id: municipio_id,
        peso_total_kg: peso_total,
        valor_declarado: totales.subtotal
      })
    });
    // Renderizar opciones de envío con sus tarifas
  }
  
  // 4. Al confirmar opción → actualizar totales con tarifa real
}
```

### 4. `frontend/cart.html`

Mostrar estimado de envío por municipio (opcional, mejora UX).

---

## Flujo completo integrado

```
Usuario en Checkout
      |
      v
[1] Cargar direcciones guardadas ← GET /api/direcciones
      |
      v
[2] Seleccionar o crear dirección
      |   (Si crea nueva → POST /api/direcciones)
      v
[3] Seleccionar departamento → municipio (DIVIPOLA)
      |
      v
[4] Cotizar envío ← POST /api/envios/cotizar
      |             Body: {municipio_id, peso_total, valor_declarado}
      v
[5] Ver opciones de transportadoras con tarifas reales
      |
      v
[6] Seleccionar opción → actualiza total en resumen
      |
      v
[7] Confirmar orden → POST /api/ordenes
      |               Incluye: dirección, opción de envío, tarifa seleccionada
      v
[8] Equipo 1 confirma orden → nosotros recibimos pedido_id
      |
      v
[9] Nuestro Módulo 5 crea seguimiento ← ya configurado
```

---

## Lo que necesitamos del Equipo 1 para hacer la integración

1. **URL base del servicio en Render** (ej: `https://marketplace-equipo1.onrender.com`)
2. **Formato exacto del body** de `POST /api/envios/cotizar`
3. **Formato del body** de `POST /api/ordenes` (si tienen ese endpoint)
4. Confirmar si requieren el `pedido_id` al crear el seguimiento o si ellos lo generan

---

## Prioridad de implementación

| Prioridad | Tarea |
|---|---|
| Alta | Agregar URL en config.js |
| Alta | Cotización de envío en checkout (reemplaza cálculo fijo) |
| Alta | Selector de dirección guardada |
| Media | Selector DIVIPOLA (departamento/municipio) |
| Baja | Gestión completa de direcciones (CRUD) |
