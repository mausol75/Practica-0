/**
 * login.js — Lógica del formulario de login.
 *
 * - Validación del lado del cliente (RF-002, RF-003)
 * - Fetch a POST /api/login
 * - Manejo de respuestas 200, 400, 401, 429
 * - Toggle de visibilidad de contraseña
 * - Rate limit visual (BR-011)
 */

(function () {
    "use strict";

    // DOM elements
    const form = document.getElementById("login-form");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const btnLogin = document.getElementById("btn-login");
    const alertContainer = document.getElementById("alert-container");
    const togglePasswordBtn = document.getElementById("toggle-password");
    const lockoutMessage = document.getElementById("lockout-message");
    const lockoutText = document.getElementById("lockout-text");

    // Error spans
    const errorUsername = document.getElementById("error-username");
    const errorPassword = document.getElementById("error-password");

    // State
    let isSubmitting = false;
    let lockoutTimer = null;

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    function showAlert(message, type = "error") {
        alertContainer.innerHTML = `<div class="alert alert--${type}">${escapeHtml(message)}</div>`;
    }

    function clearAlert() {
        alertContainer.innerHTML = "";
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    function setFieldError(group, errorSpan, message) {
        group.classList.add("has-error");
        errorSpan.textContent = message;
    }

    function clearFieldError(group, errorSpan) {
        group.classList.remove("has-error");
        errorSpan.textContent = "";
    }

    function setLoading(loading) {
        isSubmitting = loading;
        btnLogin.disabled = loading;
        if (loading) {
            btnLogin.classList.add("is-loading");
        } else {
            btnLogin.classList.remove("is-loading");
        }
    }

    // -------------------------------------------------------------------------
    // Validation (client-side mirrors server rules)
    // -------------------------------------------------------------------------

    function validateForm() {
        let valid = true;
        const groupUsername = document.getElementById("group-username");
        const groupPassword = document.getElementById("group-password");

        clearFieldError(groupUsername, errorUsername);
        clearFieldError(groupPassword, errorPassword);

        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        // Username validation (RF-002, BR-001, BR-002)
        if (!username) {
            setFieldError(groupUsername, errorUsername, "El username es obligatorio.");
            valid = false;
        } else if (username.length < 3) {
            setFieldError(groupUsername, errorUsername, "El username debe tener al menos 3 caracteres.");
            valid = false;
        } else if (username.length > 50) {
            setFieldError(groupUsername, errorUsername, "El username no debe superar los 50 caracteres.");
            valid = false;
        }

        // Password validation (RF-003, BR-003, BR-004)
        if (!password) {
            setFieldError(groupPassword, errorPassword, "La contraseña es obligatoria.");
            valid = false;
        } else if (password.length < 8) {
            setFieldError(groupPassword, errorPassword, "La contraseña debe tener al menos 8 caracteres.");
            valid = false;
        }

        return valid;
    }

    // -------------------------------------------------------------------------
    // Lockout UI (BR-011)
    // -------------------------------------------------------------------------

    function startLockoutCountdown(seconds) {
        lockoutMessage.style.display = "flex";
        btnLogin.disabled = true;

        let remaining = seconds;
        lockoutText.textContent = `Demasiados intentos. Espera ${remaining} segundos.`;

        if (lockoutTimer) clearInterval(lockoutTimer);

        lockoutTimer = setInterval(() => {
            remaining--;
            if (remaining <= 0) {
                clearInterval(lockoutTimer);
                lockoutTimer = null;
                lockoutMessage.style.display = "none";
                btnLogin.disabled = false;
            } else {
                lockoutText.textContent = `Demasiados intentos. Espera ${remaining} segundos.`;
            }
        }, 1000);
    }

    // -------------------------------------------------------------------------
    // Form submit
    // -------------------------------------------------------------------------

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        if (isSubmitting) return;

        clearAlert();

        if (!validateForm()) return;

        setLoading(true);

        const payload = {
            username: usernameInput.value.trim(),
            password: passwordInput.value,
        };

        try {
            const response = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok) {
                // Login exitoso → redirigir al dashboard
                showAlert("¡Login exitoso! Redirigiendo…", "success");
                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 600);
            } else if (response.status === 429) {
                // Rate limit (BR-011)
                showAlert(data.error, "warning");
                // Extraer los segundos del mensaje si es posible
                const match = data.error.match(/(\d+)\s*segundos/);
                if (match) {
                    startLockoutCountdown(parseInt(match[1], 10));
                }
            } else {
                // 400 o 401
                showAlert(data.error || "Error desconocido.");
            }
        } catch (err) {
            showAlert("Error de conexión. Verifica que el servidor esté activo.");
        } finally {
            setLoading(false);
        }
    });

    // -------------------------------------------------------------------------
    // Toggle password visibility
    // -------------------------------------------------------------------------

    togglePasswordBtn.addEventListener("click", function () {
        const isPassword = passwordInput.type === "password";
        passwordInput.type = isPassword ? "text" : "password";

        const eyeOpen = togglePasswordBtn.querySelector(".eye-open");
        const eyeClosed = togglePasswordBtn.querySelector(".eye-closed");

        if (isPassword) {
            eyeOpen.style.display = "none";
            eyeClosed.style.display = "block";
            togglePasswordBtn.setAttribute("aria-label", "Ocultar contraseña");
        } else {
            eyeOpen.style.display = "block";
            eyeClosed.style.display = "none";
            togglePasswordBtn.setAttribute("aria-label", "Mostrar contraseña");
        }
    });

    // -------------------------------------------------------------------------
    // Clear field errors on input
    // -------------------------------------------------------------------------

    usernameInput.addEventListener("input", () => {
        clearFieldError(document.getElementById("group-username"), errorUsername);
        clearAlert();
    });

    passwordInput.addEventListener("input", () => {
        clearFieldError(document.getElementById("group-password"), errorPassword);
        clearAlert();
    });
})();
