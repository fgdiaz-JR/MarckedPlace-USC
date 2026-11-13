/**
 * MARKETPLACE UNIVERSIDAD SANTIAGO DE CALI (USC)
 * Cliente API REST y Adaptador Supabase PostgREST
 * Proporciona llamadas seguras con Bearer JWT y fallback inteligente directo a Supabase.
 */

const API = {
  /**
   * Realiza una petición HTTP con el token JWT
   */
  async request(url, options = {}) {
    const token = Auth.getToken();
    const headers = {
      "Content-Type": "application/json",
      "apikey": CONFIG.supabase.publishableKey,
      ...(token ? { "Authorization": `Bearer ${token}` } : {}),
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, { ...options, headers });
      if (!response.ok) {
        const errorText = await response.text();
        let errorJson;
        try { errorJson = JSON.parse(errorText); } catch(e) {}
        throw new Error(errorJson?.message || errorJson?.detail || `Error HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn(`[API] Fallo en petición a ${url}:`, err.message);
      throw err;
    }
  },

  /**
   * Consulta directa a PostgREST en Supabase (evita bloqueos si el microservicio externo aún no está activo)
   */
  async supabaseTable(table, query = "") {
    const url = `${CONFIG.supabase.url}/rest/v1/${table}${query}`;
    return await this.request(url, {
      method: "GET",
      headers: {
        "Prefer": "return=representation"
      }
    });
  },

  /**
   * Inserción directa en tabla de Supabase
   */
  async supabaseInsert(table, data) {
    const url = `${CONFIG.supabase.url}/rest/v1/${table}`;
    return await this.request(url, {
      method: "POST",
      headers: {
        "Prefer": "return=representation"
      },
      body: JSON.stringify(data)
    });
  },

  /**
   * Actualización directa en tabla de Supabase
   */
  async supabaseUpdate(table, filterQuery, data) {
    const url = `${CONFIG.supabase.url}/rest/v1/${table}${filterQuery}`;
    return await this.request(url, {
      method: "PATCH",
      headers: {
        "Prefer": "return=representation"
      },
      body: JSON.stringify(data)
    });
  },

  /**
   * Eliminar en tabla de Supabase
   */
  async supabaseDelete(table, filterQuery) {
    const url = `${CONFIG.supabase.url}/rest/v1/${table}${filterQuery}`;
    return await this.request(url, {
      method: "DELETE",
      headers: {
        "Prefer": "return=representation"
      }
    });
  },

  // ==========================================
  // FORMATOS Y UTILIDADES GLOBALES
  // ==========================================
  
  /**
   * Formatea un número a moneda colombiana (COP)
   */
  formatCOP(amount) {
    const num = Number(amount) || 0;
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0
    }).format(num);
  },

  /**
   * Formatea fecha ISO a formato legible
   */
  formatDate(dateString) {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("es-CO", {
      dateStyle: "medium",
      timeStyle: "short"
    }).format(date);
  }
};

window.API = API;

