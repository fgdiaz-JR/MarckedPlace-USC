/**
 * MARKETPLACE UNIVERSIDAD SANTIAGO DE CALI (USC)
 * Configuración centralizada de microservicios y Supabase
 * Permite cambiar las URLs de los equipos cuando entreguen sus despliegues.
 */

const CONFIG = {
  // Configuración oficial de Supabase
  supabase: {
    url: "https://xmrlazemifmepyahqsrz.supabase.co",
    publishableKey: "sb_publishable_BQpJ8OjTcJarh5ZIBW9mzw_OE3Ewyfk",
    jwksUrl: "https://xmrlazemifmepyahqsrz.supabase.co/auth/v1/.well-known/jwks.json"
  },

  // URLs de los Microservicios de cada Equipo
  // Al desplegar en Render / Vercel, solo se actualizan estas URLs o se leen desde localStorage
  services: {
    // Equipo 1: Órdenes de Pedido y Envíos vinculados
    orders: localStorage.getItem("USC_API_ORDERS") || "http://localhost:8001/api",
    
    // Equipo 2: Pasarela de Pago (PSE, QR, COD)
    payments: localStorage.getItem("USC_API_PAYMENTS") || "http://localhost:8002/api",
    
    // Equipo 3: Notificaciones (Desarrollado por nosotros en FastAPI)
    notifications: localStorage.getItem("USC_API_NOTIFICATIONS") || "http://localhost:8003/api",
    
    // Equipo 4: Productos, Inventario y Carrito
    inventory: localStorage.getItem("USC_API_INVENTORY") || "http://localhost:8004/api",
    
    // Equipo 5: Seguimiento de Entregas y Transportadoras
    tracking: localStorage.getItem("USC_API_TRACKING") || "http://localhost:8005/api",
    
    // Equipo 6: Contabilidad, Conciliación y Escrow (Desarrollado por nosotros en FastAPI)
    accounting: localStorage.getItem("USC_API_ACCOUNTING") || "http://localhost:8006/api",
    
    // Equipo 7: Catálogo
    catalog: localStorage.getItem("USC_API_CATALOG") || "http://localhost:8007/api"
  },

  // Reglas de negocio fijadas por la cátedra
  business: {
    taxRate: 0.19, // IVA del 19%
    freeShippingThreshold: 200000, // Envío gratis para compras > $200.000 COP
    standardShippingCost: 15000, // Costo de envío de $15.000 COP
    platformCommissionRate: 0.05, // Comisión de la plataforma 5%
    escrowReleaseHours: 72 // 72 horas para liberación automática o conformidad
  },

  // Credenciales y roles estándar compartidos
  testUsers: {
    admin: { email: "admin@usc.edu.co", role: "ADMIN" },
    vendedor: { email: "vendedor@usc.edu.co", role: "VENDEDOR" },
    comprador: { email: "comprador@usc.edu.co", role: "COMPRADOR" }
  }
};

window.CONFIG = CONFIG;

