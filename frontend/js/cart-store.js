/**
 * MARKETPLACE UNIVERSIDAD SANTIAGO DE CALI (USC)
 * Store de Carrito de Compras (Equipo 4)
 * Persistencia en LocalStorage + Reglas de negocio:
 * IVA 19%, Envío gratis si > $200.000, si no $15.000 COP
 */

const CartStore = {
  STORAGE_KEY: "usc_cart_items",

  getItems() {
    try {
      const raw = localStorage.getItem(this.STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  },

  saveItems(items) {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(items));
    if (window.UI) UI.updateCartBadge();
    this.syncWithSupabase(items);
  },

  addItem(product, quantity = 1) {
    const items = this.getItems();
    const existingIndex = items.findIndex(item => item.id === product.id);

    if (existingIndex > -1) {
      const newQty = items[existingIndex].cantidad + quantity;
      if (product.stock !== undefined && newQty > product.stock) {
        throw new Error(`Stock insuficiente. Solo quedan ${product.stock} unidades disponibles.`);
      }
      items[existingIndex].cantidad = newQty;
    } else {
      if (product.stock !== undefined && quantity > product.stock) {
        throw new Error(`Stock insuficiente. Solo quedan ${product.stock} unidades disponibles.`);
      }
      items.push({
        id: product.id,
        nombre: product.nombre,
        precio: Number(product.precio),
        imagen_url: product.imagen_url || "",
        vendedor_id: product.vendedor_id,
        sku: product.sku || "",
        stock: product.stock,
        cantidad: quantity
      });
    }

    this.saveItems(items);
    return items;
  },

  updateQuantity(productId, quantity) {
    const items = this.getItems();
    const item = items.find(i => i.id === productId);
    if (!item) return;

    if (quantity <= 0) {
      this.removeItem(productId);
      return;
    }

    if (item.stock !== undefined && quantity > item.stock) {
      throw new Error(`Solo hay ${item.stock} unidades disponibles.`);
    }

    item.cantidad = quantity;
    this.saveItems(items);
  },

  removeItem(productId) {
    let items = this.getItems();
    items = items.filter(item => item.id !== productId);
    this.saveItems(items);
  },

  clear() {
    localStorage.removeItem(this.STORAGE_KEY);
    if (window.UI) UI.updateCartBadge();
    this.syncClearSupabase();
  },

  getTotalItems() {
    return this.getItems().reduce((sum, item) => sum + item.cantidad, 0);
  },

  /**
   * Cálculo de importes bajo reglas de negocio estrictas
   */
  getTotals() {
    const items = this.getItems();
    const subtotal = items.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
    
    // Regla: 19% de impuestos
    const impuestos = Math.round(subtotal * CONFIG.business.taxRate);
    
    // Regla: Si subtotal > $200.000 envío gratis, si no $15.000 (si hay ítems)
    let costoEnvio = 0;
    if (items.length > 0) {
      costoEnvio = subtotal > CONFIG.business.freeShippingThreshold ? 0 : CONFIG.business.standardShippingCost;
    }
    
    const descuentos = 0;
    const total = subtotal + impuestos + costoEnvio - descuentos;

    return {
      subtotal,
      impuestos,
      costoEnvio,
      descuentos,
      total,
      envioGratis: subtotal > CONFIG.business.freeShippingThreshold,
      faltaParaEnvioGratis: Math.max(0, CONFIG.business.freeShippingThreshold - subtotal)
    };
  },

  /**
   * Agrupa los productos del carrito por vendedor (Requisito Equipo 4)
   */
  getItemsBySeller() {
    const items = this.getItems();
    const grouped = {};
    for (const item of items) {
      const vId = item.vendedor_id || "vendedor_general";
      if (!grouped[vId]) grouped[vId] = [];
      grouped[vId].push(item);
    }
    return grouped;
  },

  /**
   * Sincronización asíncrona con Supabase para usuarios autenticados
   */
  async syncWithSupabase(items) {
    if (!Auth.isAuthenticated()) return;
    const user = Auth.getUser();
    try {
      // Reemplazo en tabla inv_carrito_items
      await API.supabaseDelete("inv_carrito_items", `?usuario_id=eq.${user.id}`).catch(() => {});
      for (const it of items) {
        await API.supabaseInsert("inv_carrito_items", {
          usuario_id: user.id,
          producto_id: it.id,
          cantidad: it.cantidad
        }).catch(() => {});
      }
    } catch {}
  },

  async syncClearSupabase() {
    if (!Auth.isAuthenticated()) return;
    const user = Auth.getUser();
    try {
      await API.supabaseDelete("inv_carrito_items", `?usuario_id=eq.${user.id}`).catch(() => {});
    } catch {}
  }
};

window.CartStore = CartStore;

