# Respuesta Oficial al Equipo 1 — Contratos de Integración
## Proyecto: Marketplace USC | Construcción de Software II
**Fecha:** 2026-11-19
**Emite:** Grupo 3-6 (Frontend + Módulos Notificaciones, Seguimiento, Contabilidad)

---

## 1. Contrato definitivo de Inventario (Equipo 4)

**URL base confirmada:** `https://marketplace-equipo4.onrender.com`

### Reservar stock — `POST /api/inventario/reservar`

**Autenticación:** Bearer Token JWT requerido

```json
// REQUEST BODY (schema: Reserva)
{
  "referencia_id": "string (max 100 chars) — usar el numero_orden generado",
  "items": [
    {
      "producto_id": "uuid",
      "cantidad": 2
    }
  ]
}
```

```json
// RESPUESTA EXITOSA — HTTP 200
// (schema libre — confirmar con Equipo 4 el body exacto)
{ "ok": true, "reserva_id": "...", "referencia_id": "..." }

// ERROR POR FALTA DE STOCK — HTTP 422
{
  "detail": [
    {
      "loc": ["body", "items", 0],
      "msg": "Stock insuficiente",
      "type": "value_error"
    }
  ]
}
```

**Nota:** El campo `referencia_id` es el identificador de la orden en el sistema del Equipo 1. Se usa para confirmar o liberar la reserva. Usarlo como idempotency key: si se reintenta la misma reserva con el mismo `referencia_id`, el Equipo 4 debería devolver la reserva existente (confirmar este comportamiento con ellos).

---

### Confirmar reserva — `POST /api/inventario/confirmar/{referencia_id}`

Llama este endpoint cuando el pago sea exitoso (Equipo 2 confirma). Descuenta definitivamente el stock.

```
POST https://marketplace-equipo4.onrender.com/api/inventario/confirmar/{numero_orden}
Authorization: Bearer <token>

// No requiere body
// RESPUESTA — HTTP 200: confirmación exitosa
```

---

### Liberar/Compensar reserva — ruta a confirmar

El spec del Equipo 4 **no expone un endpoint explícito de liberación/cancelación**. Los endpoints disponibles en inventario son:

```
POST /api/inventario/reservar
POST /api/inventario/confirmar/{referencia_id}
POST /api/inventario/productos/{producto_id}/movimientos   ← puede usarse para compensar
```

**Recomendación para el Equipo 1:** usar `POST /api/inventario/productos/{producto_id}/movimientos` con tipo `AJUSTE` y cantidad positiva para devolver stock manualmente cuando falle la orden o el pago:

```json
POST /api/inventario/productos/{producto_id}/movimientos
Authorization: Bearer <token>

{
  "tipo": "AJUSTE",
  "cantidad": 2,
  "nota": "Compensacion por cancelacion de orden {numero_orden}"
}
```

**Accion requerida:** Equipo 1 debe coordinar con Equipo 4 para que implementen `DELETE /api/inventario/reservar/{referencia_id}` o `POST /api/inventario/liberar/{referencia_id}`.

---

## 2. Validación contra Catálogo (Equipo 7 y Equipo 4)

### Verificar que el producto existe y obtener precio real

```
GET https://marketplace-equipo4.onrender.com/api/productos/{producto_id}

// RESPUESTA HTTP 200 — campos relevantes:
{
  "id": "uuid",
  "sku": "string",
  "nombre": "string",
  "precio": 150000.00,          // ← precio a validar
  "stock": 10,
  "activo": true,
  "vendedor_id": "uuid",        // ← validar que coincide con el vendedor del pedido
  "categoria_id": "uuid"
}

// RESPUESTA HTTP 404 — producto no existe
```

### Validación de precio y vendedor que debe hacer Equipo 1

```python
# Pseudocódigo de validación en el backend del Equipo 1
producto = GET /api/productos/{producto_id}

if not producto.activo:
    raise 400 "Producto no disponible"

if producto.vendedor_id != pedido.vendedor_id:
    raise 400 "El producto no pertenece al vendedor indicado"

# Tolerancia de precio: diferencia <= 1 COP (por redondeo)
if abs(float(producto.precio) - float(item.precio_unitario)) > 1:
    raise 400 f"Precio incorrecto. Precio real: {producto.precio}"
```

### Validar carrito completo — `POST /api/carrito/validar`

El Equipo 4 tiene este endpoint que valida todos los items de un carrito de una vez:

```
POST https://marketplace-equipo4.onrender.com/api/carrito/validar
Authorization: Bearer <token>

// Body: lista de items
[
  { "producto_id": "uuid", "cantidad": 2 },
  { "producto_id": "uuid", "cantidad": 1 }
]
```

---

## 3. Peso en Seguimiento

**Situación actual:** El Equipo 1 envía `peso_kg: null` al crear el seguimiento.

**Solución — calcular peso_total antes de llamar a Seguimiento:**

```python
# En el backend del Equipo 1, al confirmar la orden
peso_total = sum(
    item.cantidad * item.peso_kg
    for item in items_orden
    if item.peso_kg is not None
)

# Llamada a nuestro Módulo 5
POST https://marketplace-usc-seguimiento.onrender.com/api/seguimiento/crear
{
  "pedido_id": orden.id,
  "vendedor_id": orden.vendedor_id,
  "comprador_id": orden.comprador_id,
  "origen": "Cali",
  "destino": orden.municipio_destino,
  "direccion_entrega": orden.direccion_entrega,
  "peso_kg": peso_total,          // ← ya no es null
  "valor_declarado": orden.total_bruto,
  "transportadora": opcion_envio_seleccionada
}
```

El peso por producto está disponible en Equipo 4 vía `GET /api/productos/{id}` (campo `peso_kg` si existe) o en el endpoint de envío del Equipo 1 mismo (`/api/productos/{id}/envio`).

---

## 4. Variables de Entorno para el Equipo 1

```bash
# Supabase (proyecto propio del Equipo 1)
SUPABASE_URL=https://<proyecto-equipo1>.supabase.co
SUPABASE_KEY=<service_role_key>          # solo en servidor, nunca en cliente

# Inventario (Equipo 4)
URL_INVENTARIO=https://marketplace-equipo4.onrender.com/api
INVENTARIO_RESERVE_PATH=/inventario/reservar
INVENTARIO_CONFIRM_PATH=/inventario/confirmar

# Validacion de producto (Equipo 4)
URL_CATALOGO_VALIDAR=https://marketplace-equipo4.onrender.com/api/productos

# Modulos propios de nuestro grupo
URL_SEGUIMIENTO=https://marketplace-usc-seguimiento.onrender.com/api
URL_NOTIFICACIONES=https://marketplace-usc-notificaciones.onrender.com/api
URL_CONTABILIDAD=https://marketplace-usc-contabilidad.onrender.com/api
```

---

## 5. Idempotencia — Nuestros Módulos

### Módulo 5 — Seguimiento (`ent_seguimientos`)

```sql
-- La tabla tiene UNIQUE en pedido_id
-- Si se llama dos veces con el mismo pedido_id devuelve error 400 (clave duplicada)
-- Equipo 1 debe manejar ese 400 como "seguimiento ya creado" y continuar
```

**Recomendación para Equipo 1:**

```python
try:
    r = POST /api/seguimiento/crear { pedido_id: orden.id, ... }
    seguimiento_creado = r.json()
except HTTPError as e:
    if e.status_code == 400 and "duplicate" in e.detail:
        # Ya existia — consultar el existente
        seguimiento_creado = GET /api/seguimiento/pedido/{orden.id}
```

### Módulo 6 — Contabilidad (`cont_escrow`)

Actualmente **no tiene control de idempotencia** sobre `pedido_id`. Si se llama dos veces a `/escrow/retener` con el mismo `pedido_id`, se crean dos registros.

**Accion nuestra:** Agregaremos un check antes del insert. Ver sección 6.

---

## 6. Fix de Idempotencia en Contabilidad (nuestro commit)

Agregaremos en `crear_retencion_escrow()`:

```python
# Verificar si ya existe un escrow para este pedido
existing = db.table("cont_escrow").select("id").eq("pedido_id", data.pedido_id).execute()
if existing.data:
    return existing.data[0]  # devolver el existente sin crear otro
```

---

## 7. Flujo de confirmacion de orden — secuencia recomendada

```
Equipo 1 — backend al confirmar orden:

1. GET /api/productos/{id}          ← validar precio y vendedor (Equipo 4)
2. POST /api/carrito/validar        ← validar stock disponible (Equipo 4)
3. POST /api/inventario/reservar    ← reservar stock (Equipo 4)
        |
        | Si falla → abort (no crear orden)
        v
4. INSERT orden en Supabase Equipo 1
        |
        | Si falla → POST /api/inventario/productos/{id}/movimientos (AJUSTE para liberar)
        v
5. POST /api/contabilidad/escrow/retener  ← retener fondos (nuestro Módulo 6)
6. POST /api/seguimiento/crear            ← crear seguimiento (nuestro Módulo 5)
7. POST /api/notificaciones               ← notificar comprador "Orden confirmada"
8. POST /api/notificaciones               ← notificar vendedor "Nueva orden recibida"
9. POST /api/inventario/confirmar/{ref}   ← descuento definitivo de stock (Equipo 4)
```

---

## 8. Pruebas de Integración — Usuarios de Prueba

```
Supabase Central: https://xmrlazemifmepyahqsrz.supabase.co

Comprador:  comprador@usc.edu.co  / [password]  → rol COMPRADOR
Vendedor:   vendedor@usc.edu.co   / [password]  → rol VENDEDOR
Admin:      admin@usc.edu.co      / [password]  → rol ADMIN

JWKS para validar tokens:
  https://xmrlazemifmepyahqsrz.supabase.co/auth/v1/.well-known/jwks.json

Rol seguro en JWT: app_metadata.role (NO user_metadata.role)
```

---

## Resumen ejecutivo para el Equipo 1

| Punto | Estado | Accion requerida |
|---|---|---|
| Ruta reservar stock | CONFIRMADA: `POST /api/inventario/reservar` | Usar schema `Reserva` |
| Ruta confirmar stock | CONFIRMADA: `POST /api/inventario/confirmar/{referencia_id}` | Llamar cuando pago OK |
| Ruta liberar/compensar | NO EXISTE aun en Equipo 4 | Coordinar con Equipo 4 o usar AJUSTE |
| Validar producto existe | CONFIRMADA: `GET /api/productos/{id}` | Comparar precio y vendedor_id |
| Validar carrito | CONFIRMADA: `POST /api/carrito/validar` | Usar antes de reservar |
| Peso en Seguimiento | SOLUCIONABLE | Calcular suma de pesos en items |
| Idempotencia Seguimiento | MANEJABLE | Capturar 400 duplicate como "ya existe" |
| Idempotencia Contabilidad | PENDIENTE FIX | Nuestro commit lo resuelve hoy |
| Variables de entorno | DOCUMENTADAS | Ver sección 4 |
