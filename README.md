# MARKETPLACE USC - CONSTRUCCIÓN DE SOFTWARE II
**Universidad Santiago de Cali (USC)**  
**Arquitectura Global, Frontend y Servicios Centrales**  
**Lead Software & Frontend Architect:** Antigravity

---

## 1. Visión General del Proyecto
Este repositorio contiene la arquitectura completa del **Marketplace de la Universidad Santiago de Cali (USC)**:
1. **Frontend Completo (HTML/CSS/JS Nativo):** Diseñado e implementado con el sistema de diseño oficial **Versand (`Estilos_Marketplace_USC`)**, soporte nativo de modo oscuro, responsive design, autenticación JWT contra Supabase Auth y enrutamiento dinámico basado en roles (`ADMIN`, `VENDEDOR / REPARTIDOR`, `COMPRADOR`).
2. **Backends Propios en Python con FastAPI:**
   - **Equipo 3: Notificaciones** (Avisos derivados de eventos del marketplace en tiempo real).
   - **Equipo 6: Contabilidad & Escrow** (Libro diario contable, cobro de comisión del 5% de la plataforma y custodia de fondos Escrow con liberación a las 72 horas de entrega o por conformidad directa del cliente).
3. **Base de Datos Centralizada en Supabase (PostgreSQL):** Esquema maestro unificado con aislamiento por prefijos (`usr_`, `inv_`, `ord_`, `pag_`, `notif_`, `ent_`, `cont_`), sin colisiones entre grupos y con RLS habilitado.
4. **Guías Técnicas para Equipos Externos (Equipos 1, 2, 4, 5 y 7):** Documentación individual paso a paso con contratos REST, scripts SQL, mapeo de dependencias inter-módulos y especificación de entregables.

---

## 2. Estructura de Directorios
```
MarcketPlaceUSC/
├── .gitignore
├── README.md                           # Documentación técnica general
├── supabase_schema.sql                 # Script SQL maestro para el SQL Editor de Supabase
│
├── frontend/                           # Aplicación Web Frontend (HTML/CSS/JS Nativo)
│   ├── index.html                      # Redirección dinámica por sesión
│   ├── login.html                      # Inicio de sesión con JWT y botones de autocompletado
│   ├── catalog.html                    # Catálogo con búsqueda, filtros y ordenamiento (Eq. 7 & 4)
│   ├── cart.html                       # Carrito con cálculo de IVA (19%) y envío ($15k o gratis >$200k)
│   ├── checkout.html                   # Checkout y pasarela simulada (PSE, QR, Contra Entrega) (Eq. 1 & 2)
│   ├── orders.html                     # Historial de pedidos y comprobantes (Eq. 1)
│   ├── tracking.html                   # Trazabilidad de envíos, alerta 48h, llamadas y Escrow (Eq. 5)
│   ├── notifications.html              # Bandeja de avisos en plataforma (Eq. 3)
│   ├── seller-dashboard.html           # Panel de ventas, inventario y repartos (Vendedor / Repartidor)
│   ├── admin-accounting.html           # Resumen financiero, comisiones 5% y custodia Escrow (Eq. 6 & Admin)
│   ├── styles/
│   │   ├── versand.css                 # Tokens CSS, reset, tipografía y modo oscuro
│   │   └── app.css                     # Extensiones de componentes para Marketplace USC
│   └── js/
│       ├── config.js                   # Configuración de URLs de microservicios y Supabase
│       ├── auth.js                     # Cliente de autenticación Supabase Auth y guardia de roles
│       ├── api.js                      # Cliente REST con token Bearer y fallback a Supabase
│       ├── cart-store.js               # Carrito en LocalStorage y sincronización
│       ├── ui.js                       # Logotipo vectorial, temas, toasts y cabecera
│       └── modules/
│           └── catalog.js              # Lógica de renderizado dinámico de productos
│
├── backend/
│   ├── notificaciones/                 # Microservicio Equipo 3 (Python FastAPI)
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   ├── services.py
│   │   ├── requirements.txt
│   │   ├── Procfile
│   │   └── render.yaml
│   │
│   └── contabilidad/                   # Microservicio Equipo 6 (Python FastAPI)
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── schemas.py
│       ├── services.py
│       ├── requirements.txt
│       ├── Procfile
│       └── render.yaml
│
└── guias_equipos/                      # Guías individuales (Excluidas del repo de entrega)
    ├── GUIA_EQUIPO_1.md
    ├── GUIA_EQUIPO_2.md
    ├── GUIA_EQUIPO_4.md
    ├── GUIA_EQUIPO_5.md
    └── GUIA_EQUIPO_7.md
```

---

## 3. Credenciales de Prueba Oficiales
Los usuarios ya se encuentran creados y confirmados en Supabase Auth con sus roles oficiales:

| Rol Oficial | Correo Institucional | Contraseña | Redirección Inicial |
| :--- | :--- | :--- | :--- |
| **ADMIN** | `admin@usc.edu.co` | `Admin123!` | `admin-accounting.html` (Contabilidad y métricas globales) |
| **VENDEDOR / REPARTIDOR** | `vendedor@usc.edu.co` | `Vendedor123!` | `seller-dashboard.html` (Inventario, despacho y entregas) |
| **COMPRADOR** | `comprador@usc.edu.co` | `Comprador123!` | `catalog.html` (Catálogo, carrito y pedidos) |

*Nota:* En la página `login.html` se han colocado botones rápidos de autocompletado para facilitar las pruebas de la cátedra.

---

## 4. Inicialización de la Base de Datos en Supabase
1. Ingresa a tu proyecto de Supabase:  
   `https://supabase.com/dashboard/project/xmrlazemifmepyahqsrz/sql/new`
2. Abre el archivo **`supabase_schema.sql`** ubicado en la raíz de este proyecto.
3. Copia todo su contenido, pégalo en el editor SQL de Supabase y presiona **RUN**.
4. El script creará todas las tablas con sus prefijos (`usr_`, `inv_`, `ord_`, `pag_`, `notif_`, `ent_`, `cont_`), los triggers de usuarios, políticas RLS y los datos iniciales de categorías y perfiles.

---

## 5. Ejecución Local de los Backends (FastAPI)

### A. Notificaciones (Puerto 8003)
```bash
cd backend/notificaciones
pip install -r requirements.txt
uvicorn main:app --port 8003 --reload
```
Documentación interactiva Swagger: `http://localhost:8003/docs`

### B. Contabilidad & Escrow (Puerto 8006)
```bash
cd backend/contabilidad
pip install -r requirements.txt
uvicorn main:app --port 8006 --reload
```
Documentación interactiva Swagger: `http://localhost:8006/docs`

---

## 6. Ejecución del Frontend
Al ser **HTML/CSS/JS nativo**, no requiere proceso de compilación (`build`). Puedes servir la carpeta `frontend/` con cualquier servidor estático local:
```bash
# Opción con Python:
cd frontend
python -m http.server 3000

# O utilizando la extensión 'Live Server' de VS Code abriendo 'frontend/login.html'
```
Luego abre tu navegador en `http://localhost:3000/login.html`.

---

## 7. Despliegue en la Nube
- **Frontend:** Listo para desplegar en **GitHub Pages**, **Vercel** o **Render Static Site** apuntando al directorio `frontend/`.
- **Backend Notificaciones:** Listo para desplegar en **Render (Web Service)** vinculando la carpeta `backend/notificaciones/` mediante su archivo `render.yaml`.
- **Backend Contabilidad:** Listo para desplegar en **Render (Web Service)** vinculando la carpeta `backend/contabilidad/` mediante su archivo `render.yaml`.

---

## 8. Conexión con los Demás Equipos (1, 2, 4, 5 y 7)
Cuando cada equipo entregue la URL de su microservicio desplegado en Render o Vercel:
1. Abre el archivo `frontend/js/config.js`.
2. Actualiza la propiedad correspondiente en el objeto `services`:
   ```javascript
   services: {
     orders: "https://url-entregada-equipo-1.onrender.com/api",
     payments: "https://url-entregada-equipo-2.onrender.com/api",
     notifications: "https://url-entregada-equipo-3.onrender.com/api",
     inventory: "https://url-entregada-equipo-4.onrender.com/api",
     tracking: "https://url-entregada-equipo-5.onrender.com/api",
     accounting: "https://url-entregada-equipo-6.onrender.com/api",
     catalog: "https://url-entregada-equipo-7.onrender.com/api"
   }
   ```
*(O guárdalas dinámicamente en el LocalStorage del navegador mediante las llaves `USC_API_ORDERS`, `USC_API_PAYMENTS`, etc.).*
Mientras los equipos externos despliegan sus servicios, el Frontend cuenta con un adaptador PostgREST en `frontend/js/api.js` que interactúa directamente con Supabase, evitando bloqueos o caídas.

