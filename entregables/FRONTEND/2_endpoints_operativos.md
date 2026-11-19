# ENTREGABLE 2 — Endpoints Operativos REALES
## Proyecto: Marketplace USC | Repo Principal (Frontend)
**Fecha:** 2026-11-13

---

## Estado: OPERATIVO EN PRODUCCION

### URL Principal del Frontend

| Plataforma | URL | Estado |
|---|---|---|
| Vercel (principal) | https://marcketplace-usc.vercel.app | LIVE |
| GitHub Pages | https://fgdiaz-jr.github.io/MarckedPlace-USC/login.html | LIVE |
| Repositorio GitHub | https://github.com/fgdiaz-JR/MarckedPlace-USC | Publico |

---

## Endpoints de Microservicios Propios (REALES, no MOCK)

### Modulo 3 — Notificaciones
```
BASE URL: https://marketplace-usc-notificaciones.onrender.com/api
HEALTH:   https://marketplace-usc-notificaciones.onrender.com/health
DOCS:     https://marketplace-usc-notificaciones.onrender.com/docs
```

Verificacion en vivo:
```bash
curl https://marketplace-usc-notificaciones.onrender.com/health
# Respuesta: {"status":"healthy","service":"notificaciones","team":"Equipo 3"}
```

### Modulo 5 — Seguimiento de Entregas
```
BASE URL: https://marketplace-usc-seguimiento.onrender.com/api
HEALTH:   https://marketplace-usc-seguimiento.onrender.com/health
DOCS:     https://marketplace-usc-seguimiento.onrender.com/docs
```

Verificacion en vivo:
```bash
curl https://marketplace-usc-seguimiento.onrender.com/health
# Respuesta: {"status":"healthy","service":"seguimiento_entregas","team":"Equipo 5","supabase_connected":true}
```

### Modulo 6 — Contabilidad & Escrow
```
BASE URL: https://marketplace-usc-contabilidad.onrender.com/api
HEALTH:   https://marketplace-usc-contabilidad.onrender.com/health
DOCS:     https://marketplace-usc-contabilidad.onrender.com/docs
```

Verificacion en vivo:
```bash
curl https://marketplace-usc-contabilidad.onrender.com/health
# Respuesta: {"status":"healthy","service":"contabilidad_escrow","team":"Equipo 6","commission_rate":"5.0%"}
```

---

## Endpoints de Supabase (Reales)

```
URL Central (Auth + Modulos 3 y 6):
  https://xmrlazemifmepyahqsrz.supabase.co

URL Modulo 5 (Seguimiento):
  https://zludypuqnnamouhmjfuu.supabase.co

Tablas verificadas:
  - usr_perfiles       (3 usuarios de prueba)
  - notif_mensajes     (Modulo 3)
  - cont_cuentas       (Modulo 6)
  - cont_escrow        (Modulo 6)
  - cont_movimientos   (Modulo 6)
  - ent_seguimientos   (Modulo 5)
  - ent_evidencias     (Modulo 5)
```

---

## Paginas del Frontend Operativas

| Pagina | URL | Descripcion |
|---|---|---|
| Login | /login.html | Autenticacion con Supabase |
| Catalogo | /catalog.html | Productos con filtros |
| Carrito | /cart.html | Gestion de carrito |
| Checkout | /checkout.html | Proceso de compra con calculo IVA |
| Pedidos | /orders.html | Historial de ordenes |
| Seguimiento | /tracking.html | Consulta por numero de guia |
| Notificaciones | /notifications.html | Centro de mensajes |
| Panel Vendedor | /seller-dashboard.html | Dashboard de ventas |
| Contabilidad | /admin-accounting.html | Panel escrow y movimientos |

