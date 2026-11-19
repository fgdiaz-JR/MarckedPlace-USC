/**
 * MARKETPLACE UNIVERSIDAD SANTIAGO DE CALI (USC)
 * Modulo de Catalogo — consume API real del Equipo 4 (Inventario/Productos)
 * y Equipo 7 (Catalogo de busqueda)
 *
 * Estrategia de datos:
 *   1. Intenta GET https://marketplace-equipo4.onrender.com/api/productos  (fuente principal)
 *   2. Fallback: GET https://marketplace-usc-catalogo.onrender.com/api/catalogo (Equipo 7)
 *   3. Fallback final: consulta directa a Supabase (inv_productos)
 */

document.addEventListener("DOMContentLoaded", async () => {
  UI.initHeader("catalog");

  const searchInput    = document.querySelector("#searchInput");
  const categoryFilter = document.querySelector("#categoryFilter");
  const sortFilter     = document.querySelector("#sortFilter");
  const clearFiltersBtn = document.querySelector("#clearFiltersBtn");
  const productGrid    = document.querySelector("#productGrid");
  const catalogLoading = document.querySelector("#catalogLoading");
  const catalogEmpty   = document.querySelector("#catalogEmpty");
  const cartCountBtn   = document.querySelector("#cartCountBtn");

  let allProducts  = [];
  let allCategories = [];

  function updateCartBtnCount() {
    if (cartCountBtn) cartCountBtn.textContent = CartStore.getTotalItems();
  }
  updateCartBtnCount();

  // ── Cargar categorias desde Equipo 4 ──────────────────────────────────────
  async function loadCategories() {
    try {
      const res = await fetch(`${CONFIG.services.inventory}/categorias`);
      if (res.ok) {
        const data = await res.json();
        const cats = Array.isArray(data) ? data : (data.data || []);
        allCategories = cats;
        categoryFilter.innerHTML =
          `<option value="">Todas las Categorias</option>` +
          cats.map(c => `<option value="${c.nombre || c.id}">${c.nombre}</option>`).join("");
        return;
      }
    } catch (_) {}

    // Fallback: categorias del catalogo Equipo 7
    try {
      const res2 = await fetch(`${CONFIG.services.catalog}/categorias`);
      if (res2.ok) {
        const cats2 = await res2.json();
        (Array.isArray(cats2) ? cats2 : []).forEach(c => {
          const opt = document.createElement("option");
          opt.value = c.nombre || c.id;
          opt.textContent = c.nombre;
          categoryFilter.appendChild(opt);
        });
      }
    } catch (_) {}
  }

  // ── Cargar productos ──────────────────────────────────────────────────────
  async function loadProducts() {
    catalogLoading.style.display = "block";
    catalogEmpty.style.display   = "none";
    productGrid.innerHTML        = "";

    // 1. Equipo 4 — fuente de verdad del inventario
    try {
      const res = await fetch(`${CONFIG.services.inventory}/productos`);
      if (res.ok) {
        const data = await res.json();
        allProducts = Array.isArray(data) ? data : (data.data || data.productos || []);
        if (allProducts.length > 0) {
          catalogLoading.style.display = "none";
          renderProducts();
          return;
        }
      }
    } catch (e) {
      console.warn("Equipo 4 no disponible, intentando Equipo 7:", e.message);
    }

    // 2. Equipo 7 — catalogo publico de busqueda
    try {
      const res2 = await fetch(`${CONFIG.services.catalog}/catalogo`);
      if (res2.ok) {
        const data2 = await res2.json();
        allProducts = Array.isArray(data2) ? data2 : (data2.data || []);
        if (allProducts.length > 0) {
          catalogLoading.style.display = "none";
          renderProducts();
          return;
        }
      }
    } catch (e) {
      console.warn("Equipo 7 no disponible, usando Supabase directo:", e.message);
    }

    // 3. Fallback final: Supabase directo
    try {
      const prods = await API.supabaseTable("inv_productos", "?activo=eq.true&order=creado_en.desc");
      allProducts = Array.isArray(prods) ? prods : [];
      catalogLoading.style.display = "none";
      renderProducts();
    } catch (e) {
      catalogLoading.style.display = "none";
      catalogEmpty.style.display   = "block";
      catalogEmpty.querySelector("h3").textContent = "Servicio no disponible";
      catalogEmpty.querySelector("p").textContent  =
        "El modulo de productos no responde. Intenta mas tarde o contacta al Equipo 4.";
    }
  }

  // ── Renderizar tarjetas de producto ──────────────────────────────────────
  function renderProducts() {
    const searchTerm       = (searchInput.value || "").toLowerCase().trim();
    const selectedCategory = categoryFilter.value;
    const sort             = sortFilter.value;

    let filtered = allProducts.filter(p => {
      const name  = (p.nombre || p.name || "").toLowerCase();
      const desc  = (p.descripcion || p.description || "").toLowerCase();
      const cat   = p.categoria || p.category || p.categoria_nombre || "";
      const matchSearch = name.includes(searchTerm) || desc.includes(searchTerm);
      const matchCat    = !selectedCategory || cat === selectedCategory;
      return matchSearch && matchCat;
    });

    // Ordenamiento
    if (sort === "price_asc") {
      filtered.sort((a, b) => Number(a.precio || a.price || 0) - Number(b.precio || b.price || 0));
    } else if (sort === "price_desc") {
      filtered.sort((a, b) => Number(b.precio || b.price || 0) - Number(a.precio || a.price || 0));
    } else if (sort === "name_asc") {
      filtered.sort((a, b) => (a.nombre || "").localeCompare(b.nombre || ""));
    }

    if (filtered.length === 0) {
      catalogEmpty.style.display = "block";
      productGrid.innerHTML      = "";
      return;
    }

    catalogEmpty.style.display = "none";

    productGrid.innerHTML = filtered.map(p => {
      // Normalizar campos (Equipo 4 y Equipo 7 pueden tener nombres distintos)
      const nombre    = p.nombre || p.name || "Sin nombre";
      const desc      = p.descripcion || p.description || "Articulo verificado del campus universitario.";
      const precio    = Number(p.precio || p.price || 0);
      const stock     = Number(p.stock ?? p.cantidad ?? 999);
      const sku       = p.sku || p.codigo || p.id?.slice(0, 8).toUpperCase() || "—";
      const categoria = p.categoria || p.category || p.categoria_nombre || "General";
      const imgUrl    = p.imagen_url || p.image_url || p.imagen ||
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80";
      const isOutOfStock = stock <= 0;
      const isLowStock   = !isOutOfStock && stock <= 5;

      const stockBadge = isOutOfStock
        ? `<span class="badge badge-danger">Agotado</span>`
        : isLowStock
        ? `<span class="badge badge-warning">Ultimas ${stock} unidades</span>`
        : `<span class="badge badge-success">${stock} disponibles</span>`;

      return `
        <article class="product-card" data-id="${p.id}">
          <div class="product-media">
            <img src="${imgUrl}" alt="${nombre}" loading="lazy"
              onerror="this.src='https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80'">
            <div style="position:absolute;top:10px;right:10px;">${stockBadge}</div>
          </div>
          <div class="product-body">
            <span class="product-category">${categoria} &middot; SKU: ${sku}</span>
            <h3 class="product-title">${nombre}</h3>
            <p class="product-desc">${desc}</p>
            <div class="product-footer">
              <span class="product-price">${API.formatCOP(precio)}</span>
              <button
                class="btn btn-primary add-to-cart-btn"
                data-id="${p.id}"
                data-nombre="${nombre}"
                data-precio="${precio}"
                data-stock="${stock}"
                ${isOutOfStock ? "disabled" : ""}
                style="${isOutOfStock ? "opacity:0.5;cursor:not-allowed;" : ""}">
                ${isOutOfStock ? "Agotado" : "Agregar al carrito"}
              </button>
            </div>
          </div>
        </article>
      `;
    }).join("");

    // Listeners agregar al carrito
    document.querySelectorAll(".add-to-cart-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const prod = allProducts.find(p => p.id === btn.dataset.id);
        if (!prod) return;
        try {
          CartStore.addItem(prod, 1);
          UI.toast(`"${btn.dataset.nombre}" agregado al carrito.`, "success");
          updateCartBtnCount();
          UI.updateCartBadge();
        } catch (err) {
          UI.toast(err.message, "danger");
        }
      });
    });
  }

  // ── Escucha de filtros ────────────────────────────────────────────────────
  searchInput.addEventListener("input", renderProducts);
  categoryFilter.addEventListener("change", renderProducts);
  sortFilter.addEventListener("change", renderProducts);
  clearFiltersBtn.addEventListener("click", () => {
    searchInput.value    = "";
    categoryFilter.value = "";
    sortFilter.value     = "recent";
    renderProducts();
  });

  await loadCategories();
  await loadProducts();
});
