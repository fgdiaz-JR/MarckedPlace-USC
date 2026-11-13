/**
 * MARKETPLACE UNIVERSIDAD SANTIAGO DE CALI (USC)
 * Módulo de Autenticación JWT con Supabase Auth Nativo
 */

const Auth = {
  TOKEN_KEY: "usc_auth_token",
  USER_KEY: "usc_auth_user",

  /**
   * Inicia sesión contra Supabase Auth nativo
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
      throw new Error(errData.error_description || errData.msg || "Credenciales inválidas. Verifica tu correo y contraseña.");
    }

    const data = await response.json();
    
    // Extraer metadata y rol
    const user = {
      id: data.user.id,
      email: data.user.email,
      nombre: data.user.user_metadata?.nombre || data.user.email.split('@')[0],
      rol: data.user.user_metadata?.rol || "COMPRADOR"
    };

    localStorage.setItem(this.TOKEN_KEY, data.access_token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));

    return { token: data.access_token, user };
  },

  /**
   * Cierra sesión y limpia almacenamiento local
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
   * Retorna el rol del usuario actual
   */
  getRole() {
    const user = this.getUser();
    return user ? user.rol : null;
  },

  /**
   * Verifica si hay sesión activa
   */
  isAuthenticated() {
    return !!this.getToken() && !!this.getUser();
  },

  /**
   * Guardia de ruta: asegura que el usuario esté logueado y tenga uno de los roles requeridos
   */
  requireAuth(allowedRoles = []) {
    if (!this.isAuthenticated()) {
      window.location.href = "login.html";
      return false;
    }

    const currentRole = this.getRole();
    if (allowedRoles.length > 0 && !allowedRoles.includes(currentRole)) {
      alert(`Acceso denegado: tu rol (${currentRole}) no tiene permisos para esta vista.`);
      this.redirectByRole();
      return false;
    }

    return true;
  },

  /**
   * Redirección dinámica según el rol del usuario
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

