/**
 * MARKETPLACE UNIVERSIDAD SANTIAGO DE CALI (USC)
 * Componentes de UI, Toasts, Tema y Cabecera Versand
 */

const UI = {
 logoSvg: `<svg viewBox="0 0 24 24" aria-hidden="true" width="22" height="22"><path d="M4 7.5 12 4l8 3.5v9L12 20l-8-3.5v-9Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M4 7.5 12 11l8-3.5M12 11v9M8 5.75v8.5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M16.5 5.8c2.1 0 3.5 1.4 3.5 3.2 0 2.7-3.5 5.2-3.5 5.2S13 11.7 13 9c0-1.8 1.4-3.2 3.5-3.2Z" fill="currentColor" stroke="var(--surface)" stroke-width=".8"/><circle cx="16.5" cy="9" r="1" fill="var(--surface)"/></svg>`,

 /**
 * Configura el tema claro / oscuro con persistencia
 */
 initTheme() {
 const savedTheme = localStorage.getItem("usc_theme") || "light";
 document.body.dataset.theme = savedTheme;
 this.updateThemeButton();

 document.querySelectorAll(".theme-toggle-btn").forEach(btn => {
 btn.addEventListener("click", () => {
 const isDark = document.body.dataset.theme === "dark";
 const newTheme = isDark ? "light" : "dark";
 document.body.dataset.theme = newTheme;
 localStorage.setItem("usc_theme", newTheme);
 this.updateThemeButton();
 });
 });
 },

 updateThemeButton() {
 const isDark = document.body.dataset.theme === "dark";
 document.querySelectorAll(".theme-toggle-btn").forEach(btn => {
 btn.textContent = isDark ? "" : "";
 btn.setAttribute("title", isDark ? "Cambiar a modo claro" : "Cambiar a modo oscuro");
 });
 },

 /**
 * Renderiza la barra superior estándar en las vistas
 */
 initHeader(activeModule = "") {
 const user = Auth.getUser();
 const role = Auth.getRole() || "INVITADO";
 const userInitials = user?.nombre ? user.nombre.substring(0, 2).toUpperCase() : "US";

 // Insertar logos
 document.querySelectorAll(".brand-mark-slot").forEach(el => {
 el.innerHTML = this.logoSvg;
 });

 // Actualizar nombre y rol
 const userNameEl = document.querySelector("#headerUserName");
 if (userNameEl && user) {
 userNameEl.textContent = user.nombre;
 }

 const roleBadgeEl = document.querySelector("#headerRoleBadge");
 if (roleBadgeEl) {
 roleBadgeEl.textContent = role;
 }

 const avatarEl = document.querySelector("#headerAvatar");
 if (avatarEl) {
 avatarEl.textContent = userInitials;
 }

 // Configurar botón salir
 const logoutBtn = document.querySelector("#logoutBtn");
 if (logoutBtn) {
 logoutBtn.addEventListener("click", (e) => {
 e.preventDefault();
 Auth.logout();
 });
 }

 this.initTheme();
 this.updateCartBadge();
 this.updateNotificationBadge();
 },

 /**
 * Muestra un toast emergente
 */
 toast(message, type = "info") {
 let container = document.querySelector(".toast-container");
 if (!container) {
 container = document.createElement("div");
 container.className = "toast-container";
 document.body.appendChild(container);
 }

 const toast = document.createElement("div");
 toast.className = `toast ${type}`;
 toast.textContent = message;

 container.appendChild(toast);

 setTimeout(() => {
 toast.style.opacity = "0";
 toast.style.transform = "translateX(50px)";
 toast.style.transition = ".25s ease";
 setTimeout(() => toast.remove(), 250);
 }, 3500);
 },

 /**
 * Actualiza el badge del carrito en el navbar
 */
 updateCartBadge() {
 const badge = document.querySelector("#cartBadge");
 if (!badge) return;
 const count = CartStore.getTotalItems();
 badge.textContent = count;
 badge.style.display = count > 0 ? "inline-flex" : "none";
 },

 /**
 * Actualiza el badge de notificaciones
 */
 async updateNotificationBadge() {
 const badge = document.querySelector("#notifBadge");
 if (!badge || !Auth.isAuthenticated()) return;

 try {
 const user = Auth.getUser();
 // Consultar al backend de notificaciones (o Supabase directamente)
 const res = await API.supabaseTable("notif_mensajes", `?usuario_id=eq.${user.id}&leido=eq.false&select=id`);
 const unreadCount = Array.isArray(res) ? res.length : 0;
 badge.textContent = unreadCount;
 badge.style.display = unreadCount > 0 ? "inline-flex" : "none";
 } catch (e) {
 // Ignorar si la tabla aún se está creando
 }
 }
};

window.UI = UI;
