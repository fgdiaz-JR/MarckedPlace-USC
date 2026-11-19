# ENTREGABLE 1 — Contrato API v1 Acordado
## Proyecto: Marketplace USC | Módulo 5 — Seguimiento de Entregas
**Equipo:** Grupo 3 & 6 (construyó el módulo por encargo)
**Fecha:** 2026-11-13
**URL Servicio:** https://marketplace-usc-seguimiento.onrender.com
**Supabase:** https://zludypuqnnamouhmjfuu.supabase.co

---

## Descripción del Módulo

El **Módulo 5** gestiona el ciclo de vida completo de un envío: desde la confirmación del pedido hasta la entrega física, incluyendo evidencia fotográfica y PQR.

---

## Contrato de API v1

### Base URL
```
https://marketplace-usc-seguimiento.onrender.com
```

### Versión
```
v1.0.0 — 2026-11-13
```

### Autenticación
```
Tipo: Bearer Token (JWT Supabase)
Header: Authorization: Bearer <token>
Nota: Los endpoints son públicos en esta fase v1 (sin validación de token requerida)
```

---

## Endpoints Acordados

### GET `/health`
Verificación de estado del servicio.

**Respuesta 200:**
```json
{
  "status": "healthy",
  "service": "seguimiento_entregas",
  "team": "Equipo 5",
  "version": "1.0.0",
  "supabase_connected": true
}
```

---

### POST `/api/seguimiento/crear`
Crea un nuevo seguimiento al confirmar un pedido.

**Request Body:**
```json
{
  "pedido_id": "uuid-string",
  "vendedor_id": "uuid-string",
  "comprador_id": "uuid-string",
  "origen": "string",
  "destino": "string",
  "direccion_entrega": "string",
  "transportadora": "string | null",
  "peso_kg": "float | null",
  "valor_declarado": "float | null",
  "numero_guia": "string | null",
  "observaciones": "string | null"
}
```

**Respuesta 200:**
```json
{
  "success": true,
  "data": { "...campos del seguimiento creado..." }
}
```

---

### GET `/api/seguimiento/pedido/{pedido_id}`
Consulta el seguimiento de un pedido específico.

**Parámetro:** `pedido_id` (UUID del pedido — lo provee Equipo 1)

**Respuesta 200:**
```json
{
  "success": true,
  "data": { "...campos del seguimiento..." }
}
```

**Respuesta 404:**
```json
{ "detail": "No hay seguimiento para el pedido {pedido_id}" }
```

---

### GET `/api/seguimiento?numero_guia={guia}`
Consulta el estado de un envío por número de guía.

---

### GET `/api/seguimiento/comprador/{comprador_id}`
Lista todos los envíos de un comprador.

---

### GET `/api/seguimiento/vendedor/{vendedor_id}`
Lista todos los envíos de un vendedor.

---

### PUT `/api/seguimiento/{numero_guia}/estado`
Actualiza el estado del envío.

**Request Body:**
```json
{
  "estado": "EN_TRANSITO",
  "ubicacion_actual": "string | null",
  "observaciones": "string | null"
}
```

**Estados válidos:**
```
PENDIENTE | RECOGIDO | EN_TRANSITO | EN_DESTINO | ENTREGADO | FALLIDO | DEVOLUCION
```

---

### POST `/api/seguimiento/{numero_guia}/entregar`
Registra la entrega exitosa. Dispara notificación al comprador y el contador de 72h en Escrow.

**Request Body:**
```json
{
  "foto_evidencia_url": "string | null",
  "receptor_nombre": "string | null",
  "receptor_documento": "string | null",
  "observaciones": "string | null"
}
```

---

### POST `/api/seguimiento/{numero_guia}/pqr`
Reporta un incidente. Congela el escrow en Módulo 6.

**Request Body:**
```json
{
  "tipo_pqr": "PERDIDA | DANO | RETRASO | ENTREGA_INCORRECTA | OTRO",
  "descripcion": "string (min 10 chars)",
  "evidencia_url": "string | null"
}
```

---

## Dependencias inter-módulos acordadas

| Evento | Acción | Destino |
|---|---|---|
| Estado = ENTREGADO | Llama escrow/marcar-entrega | Módulo 6 |
| PQR reportada | Llama escrow/bloquear | Módulo 6 |
| Estado = EN_TRANSITO / EN_DESTINO | Envia notificación | Módulo 3 |
| Pedido confirmado | Equipo 1 llama /crear | Este módulo |

---

## Esquema de Base de Datos

**Proyecto Supabase:** `zludypuqnnamouhmjfuu`

### Tabla `ent_seguimientos`
| Campo | Tipo | Descripcion |
|---|---|---|
| id | UUID | Clave primaria |
| pedido_id | UUID | Referencia al pedido (Equipo 1) |
| vendedor_id | UUID | Referencia al vendedor |
| comprador_id | UUID | Referencia al comprador |
| numero_guia | VARCHAR(80) | Generado automaticamente USC-XXXXXXXX |
| transportadora | VARCHAR(100) | Nombre de la empresa de transporte |
| estado | VARCHAR(40) | Estado actual del envio |
| origen | VARCHAR(120) | Ciudad de origen |
| destino | VARCHAR(120) | Ciudad de destino |
| direccion_entrega | TEXT | Direccion completa |
| peso_kg | NUMERIC | Peso del paquete |
| valor_declarado | NUMERIC | Valor declarado en COP |
| fecha_estimada_entrega | TIMESTAMPTZ | Fecha estimada |
| fecha_entrega_real | TIMESTAMPTZ | Fecha real de entrega |
| receptor_nombre | VARCHAR(200) | Quien recibio el paquete |
| receptor_documento | VARCHAR(50) | Documento del receptor |
| created_at | TIMESTAMPTZ | Fecha de creacion |
| updated_at | TIMESTAMPTZ | Ultima actualizacion |

### Tabla `ent_evidencias`
| Campo | Tipo | Descripcion |
|---|---|---|
| id | UUID | Clave primaria |
| seguimiento_id | UUID | Referencia a ent_seguimientos |
| tipo_evidencia | VARCHAR(50) | FOTO_ENTREGA, PQR_DANO, etc. |
| url_archivo | TEXT | URL de la imagen o documento |
| descripcion | TEXT | Descripcion del archivo |
| created_at | TIMESTAMPTZ | Fecha de registro |

