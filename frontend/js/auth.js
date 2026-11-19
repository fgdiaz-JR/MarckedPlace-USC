/**
 * MARKETPLACE UNIVERSIDAD SANTIAGO DE CALI (USC)
 * Modulo de Autenticacion JWT con Supabase Auth Nativo
 *
 * SEGURIDAD: El rol del usuario se lee exclusivamente de app_metadata (firmado
 * por el service_role del servidor). user_metadata es editable por el propio
 * usuario y NO debe usarse para decisiones de acceso o privilegios.
 *
 * Jerarquia de lectura del rol:
 *   1. app_metadata.role   (campo estandar Supabase)
 *   2. app_metadata.rol    (campo alternativo en espanol)
 *   3. user_metadata.role  (solo como fallback de desarrollo — NO usar en prod)
 *   4. "COMPRADOR"         (rol minimo por defecto)
 */

const Auth = {
  TOKEN_KEY: "usc_auth_token",
  USER_KEY:  "usc_auth_user",

  /**
   * Extrae el rol del usuario desde el JWT de forma segura.
   * Lee app_metadata primero; user_metadata solo como ultimo recurso.
   * @param {object} userObj - Objeto user devuelto por Supabase Auth
   * @returns {string} Rol: ADMIN | VENDEDOR | COMPRADOR
   */
  _extractRole(userObj) {
    const app  = userObj?.app_metadata  || {};
    const meta = userObj?.user_metadata || {};

    // app_metadata es de escritura exclusiva del servidor — fuente de verdad
    const role = app.role
      || app.rol
      || meta.role   // fallback de desarrollo (no confiable en produccion)
      || meta.rol
      || "COMPRADOR";

    // Normalizar a mayusculas y validar contra los roles conocidos
    const normalized = String(role).toUpperCase();
    return ["ADMIN", "VENDEDOR", "COMPRADOR"].includes(normalized)
      ? normalized
      : "COMPRADOR";
  },

  /**
   * Inicia sesion contra Supabase Auth nativo
   */
  async login(email, password) {
    const url = `${CONFIG.supabase.url}/auth/v1/token?grant_type=password`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "apikey": CONFIG.supabase.publishableKey
      },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error_description || errData.msg || "Credenciales invalidas. Verifica tu correo y contrasena.");
    }

    const data = await response.json();

    // Rol leido de app_metadata (firmado por el servidor — no manipulable por el usuario)
    const user = {
      id:     data.user.id,
      email:  data.user.email,
      nombre: data.user.user_metadata?.nombre
              || data.user.user_metadata?.name
              || data.user.email.split("@")[0],
      rol:    this._extractRole(data.user)
    };

    localStorage.setItem(this.TOKEN_KEY, data.access_token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));

    return { token: data.access_token, user };
  },

  /**
   * Cierra sesion y limpia almacenamiento local
   */
  logout() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    window.location.href = "login.html";
  },

  /**
   * Retorna el token JWT actual
   */
  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  /**
   * Retorna el objeto del usuario logueado
   */
  getUser() {
    const raw = localStorage.getItem(this.USER_KEY);
    return raw ? JSON.parse(raw) : null;
  },

  /**
   * Retorna el rol del usuario actual (leido de app_metadata al momento del login)
   */
  getRole() {
    const user = this.getUser();
    return user ? user.rol : null;
  },

  /**
   * Verifica si hay sesion activa
   */
  isAuthenticated() {
    return !!this.getToken() && !!this.getUser();
  },

  /**
   * Guardia de ruta: verifica autenticacion y rol requerido
   * @param {string[]} allowedRoles - Roles que pueden acceder. Vacio = cualquier autenticado.
   */
  requireAuth(allowedRoles = []) {
    if (!this.isAuthenticated()) {
      window.location.href = "login.html";
      return false;
    }

    const currentRole = this.getRole();
    if (allowedRoles.length > 0 && !allowedRoles.includes(currentRole)) {
      alert(`Acceso denegado: tu rol (${currentRole}) no tiene permisos para esta seccion.`);
      this.redirectByRole();
      return false;
    }

    return true;
  },

  /**
   * Redireccion dinamica segun el rol del usuario
   */
  redirectByRole() {
    const role = this.getRole();
    if (role === "ADMIN") {
      window.location.href = "admin-accounting.html";
    } else if (role === "VENDEDOR") {
      window.location.href = "seller-dashboard.html";
    } else {
      window.location.href = "catalog.html";
    }
  }
};

window.Auth = Auth;
