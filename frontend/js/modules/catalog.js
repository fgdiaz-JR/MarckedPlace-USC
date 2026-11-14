/**
 * MARKETPLACE UNIVERSIDAD SANTIAGO DE CALI (USC)
 * Módulo de Catálogo (Equipo 7) e Inventario (Equipo 4)
 */

document.addEventListener("DOMContentLoaded", async () => {
 UI.initHeader("catalog");

 const searchInput = document.querySelector("#searchInput");
 const categoryFilter = document.querySelector("#categoryFilter");
 const sortFilter = document.querySelector("#sortFilter");
 const clearFiltersBtn = document.querySelector("#clearFiltersBtn");
 const productGrid = document.querySelector("#productGrid");
 const catalogLoading = document.querySelector("#catalogLoading");
 const catalogEmpty = document.querySelector("#catalogEmpty");
 const cartCountBtn = document.querySelector("#cartCountBtn");

 let allProducts = [];
 let allCategories = [];

 // Actualizar contador del botón del carrito
 function updateCartBtnCount() {
 if (cartCountBtn) cartCountBtn.textContent = CartStore.getTotalItems();
 }
 updateCartBtnCount();

 // Cargar categorías
 async function loadCategories() {
 try {
 // Intenta consultar la tabla inv_categorias
 const cats = await API.supabaseTable("inv_categorias", "?activo=eq.true&order=nombre.asc");
 allCategories = Array.isArray(cats) ? cats : [];
 categoryFilter.innerHTML = `<option value="">Todas las Categorías</option>` + 
 allCategories.map(c => `<option value="${c.id}">${c.nombre}</option>`).join("");
 } catch (e) {
 console.warn("No se pudieron cargar categorías:", e.message);
 }
 }

 // Cargar productos desde Supabase
 async function loadProducts() {
 catalogLoading.style.display = "block";
 catalogEmpty.style.display = "none";
 productGrid.innerHTML = "";

 try {
 // Consulta a la tabla inv_productos con campos de inventario y categoría
 const prods = await API.supabaseTable("inv_productos", "?activo=eq.true&order=creado_en.desc");
 allProducts = Array.isArray(prods) ? prods : [];
 catalogLoading.style.display = "none";
 renderProducts();
 } catch (e) {
 catalogLoading.style.display = "none";
 catalogEmpty.style.display = "block";
 catalogEmpty.querySelector("h3").textContent = "Base de datos en inicialización";
 catalogEmpty.querySelector("p").textContent = "Ejecuta el script 'supabase_schema.sql' en el SQL Editor de tu panel de Supabase para activar las tablas.";
 }
 }

 // Renderizar productos aplicando filtros y ordenamiento
 function renderProducts() {
 const searchTerm = (searchInput.value || "").toLowerCase().trim();
 const selectedCategory = categoryFilter.value;
 const sort = sortFilter.value;

 let filtered = allProducts.filter(p => {
 const matchSearch = p.nombre.toLowerCase().includes(searchTerm) || 
 (p.descripcion && p.descripcion.toLowerCase().includes(searchTerm));
 const matchCat = !selectedCategory || p.categoria_id === selectedCategory;
 return matchSearch && matchCat;
 });

 // Ordenamiento
 if (sort === "price_asc") {
 filtered.sort((a, b) => Number(a.precio) - Number(b.precio));
 } else if (sort === "price_desc") {
 filtered.sort((a, b) => Number(b.precio) - Number(a.precio));
 } else if (sort === "name_asc") {
 filtered.sort((a, b) => a.nombre.localeCompare(b.nombre));
 }

 if (filtered.length === 0) {
 catalogEmpty.style.display = "block";
 productGrid.innerHTML = "";
 return;
 }

 catalogEmpty.style.display = "none";
 productGrid.innerHTML = filtered.map(p => {
 const isOutOfStock = p.stock <= 0;
 const isLowStock = !isOutOfStock && p.stock <= (p.stock_minimo_alerta || 5);

 const stockBadge = isOutOfStock
 ? `<span class="badge badge-danger">Agotado</span>`
 : isLowStock
 ? `<span class="badge badge-warning">¡Últimas ${p.stock} unidades!</span>`
 : `<span class="badge badge-success">${p.stock} disponibles</span>`;

 // Imagen predeterminada segura según categoría o placeholder SVG
 const imgUrl = p.imagen_url || "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80";

 return `
 <article class="product-card" data-id="${p.id}">
 <div class="product-media">
 <img src="${imgUrl}" alt="${p.nombre}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80'">
 <div style="position: absolute; top: 10px; right: 10px;">
 ${stockBadge}
 </div>
 </div>
 <div class="product-body">
 <span class="product-category">SKU: ${p.sku}</span>
 <h3 class="product-title">${p.nombre}</h3>
 <p class="product-desc">${p.descripcion || "Artículo verificado del campus universitario."}</p>
 <div class="product-footer">
 <span class="product-price">${API.formatCOP(p.precio)}</span>
 <button 
 class="btn btn-primary add-to-cart-btn" 
 data-id="${p.id}"
 ${isOutOfStock ? "disabled" : ""}
 style="${isOutOfStock ? "opacity:0.5; cursor:not-allowed;" : ""}">
 ${isOutOfStock ? "Agotado" : "Agregar +"}
 </button>
 </div>
 </div>
 </article>
 `;
 }).join("");

 // Event listeners para agregar al carrito
 document.querySelectorAll(".add-to-cart-btn").forEach(btn => {
 btn.addEventListener("click", (e) => {
 const prodId = btn.dataset.id;
 const prod = allProducts.find(p => p.id === prodId);
 if (!prod) return;

 try {
 CartStore.addItem(prod, 1);
 UI.toast(`Agregaste "${prod.nombre}" al carrito.`, "success");
 updateCartBtnCount();
 } catch (err) {
 UI.toast(err.message, "danger");
 }
 });
 });
 }

 // Escucha de filtros
 searchInput.addEventListener("input", renderProducts);
 categoryFilter.addEventListener("change", renderProducts);
 sortFilter.addEventListener("change", renderProducts);
 clearFiltersBtn.addEventListener("click", () => {
 searchInput.value = "";
 categoryFilter.value = "";
 sortFilter.value = "recent";
 renderProducts();
 });

 await loadCategories();
 await loadProducts();
});
