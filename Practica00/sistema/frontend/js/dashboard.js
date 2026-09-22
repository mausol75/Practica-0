/**
 * dashboard.js — Lógica del dashboard protegido.
 *
 * - Verifica la sesión al cargar (GET /api/session)
 * - Muestra el username autenticado
 * - Maneja el cierre de sesión (POST /api/logout)
 */

(function () {
    "use strict";

    const displayUsername = document.getElementById("display-username");
    const btnLogout = document.getElementById("btn-logout");

    // -------------------------------------------------------------------------
    // Verificar sesión al cargar
    // -------------------------------------------------------------------------

    async function checkSession() {
        try {
            const response = await fetch("/api/session");
            const data = await response.json();

            if (data.authenticated && data.username) {
                displayUsername.textContent = data.username;
            } else {
                // No autenticado → redirigir al login
                window.location.href = "/login";
            }
        } catch {
            window.location.href = "/login";
        }
    }

    // -------------------------------------------------------------------------
    // Logout
    // -------------------------------------------------------------------------

    btnLogout.addEventListener("click", async function () {
        btnLogout.disabled = true;
        btnLogout.style.opacity = "0.5";

        try {
            await fetch("/api/logout", { method: "POST" });
        } catch {
            // Incluso si hay error, redirigir al login
        }

        window.location.href = "/login";
    });

    // -------------------------------------------------------------------------
    // Init
    // -------------------------------------------------------------------------

    checkSession();
})();
