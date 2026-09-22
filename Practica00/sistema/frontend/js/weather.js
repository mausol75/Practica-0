/**
 * weather.js — Lógica de consulta de clima (002-Consulta-clima).
 *
 * - Envía GET /api/v1/weather?location=...
 * - Muestra resultados (temperatura, condición, humedad)
 * - Manejo de estados de carga y errores
 */

(function () {
    "use strict";

    // DOM elements
    const form = document.getElementById("weather-form");
    const locationInput = document.getElementById("weather-location");
    const btnSearch = document.getElementById("btn-weather-search");
    const alertContainer = document.getElementById("weather-alert");
    const resultCard = document.getElementById("weather-result");
    const locationName = document.getElementById("weather-location-name");
    const tempValue = document.getElementById("weather-temp");
    const conditionValue = document.getElementById("weather-condition");
    const humidityValue = document.getElementById("weather-humidity");

    let isSearching = false;

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

    function setLoading(loading) {
        isSearching = loading;
        btnSearch.disabled = loading;
        if (loading) {
            btnSearch.classList.add("is-loading");
        } else {
            btnSearch.classList.remove("is-loading");
        }
    }

    function showResult(data) {
        locationName.textContent = data.location;
        tempValue.textContent = data.temperature;
        conditionValue.textContent = data.condition;
        humidityValue.textContent = data.humidity;

        resultCard.style.display = "block";
        // Trigger entrance animation
        resultCard.classList.remove("weather-result--animate");
        // Force reflow
        void resultCard.offsetWidth;
        resultCard.classList.add("weather-result--animate");
    }

    function hideResult() {
        resultCard.style.display = "none";
    }

    // -------------------------------------------------------------------------
    // Form submit
    // -------------------------------------------------------------------------

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        if (isSearching) return;

        clearAlert();

        const location = locationInput.value.trim();
        if (!location) {
            showAlert("Ingresa un país o ciudad para consultar el clima.");
            return;
        }

        setLoading(true);
        hideResult();

        try {
            const response = await fetch(
                `/api/v1/weather?location=${encodeURIComponent(location)}`
            );
            const data = await response.json();

            if (response.ok) {
                showResult(data);
            } else if (response.status === 401) {
                // Session expired — redirect to login
                showAlert("Tu sesión ha expirado. Redirigiendo al login...", "warning");
                setTimeout(() => {
                    window.location.href = "/login";
                }, 1500);
            } else {
                showAlert(data.error || "Error al consultar el clima.");
            }
        } catch (err) {
            showAlert("Error de conexión. Verifica que el servidor esté activo.");
        } finally {
            setLoading(false);
        }
    });

    // -------------------------------------------------------------------------
    // Clear alert on input
    // -------------------------------------------------------------------------

    locationInput.addEventListener("input", () => {
        clearAlert();
    });
})();
