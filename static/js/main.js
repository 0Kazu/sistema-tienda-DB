// Atrapar los errores SQL (En realidad los triggers)
function showAlert(type, message) {
    const container = document.getElementById("alert-container");
    if (!container) return;

    const wrapper = document.createElement("div");
    wrapper.className = `alert alert-${type} alert-dismissible fade show`;
    wrapper.setAttribute("role", "alert");
    wrapper.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
    `;
    container.prepend(wrapper);
}


async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();

        if (!response.ok || data.success === false) {
            showAlert("danger", data.message || "Ocurrió un error inesperado.");
            return null;
        }
        return data;
    } catch (err) {
        showAlert("danger", "No se pudo contactar al servidor. Intenta de nuevo.");
        return null;
    }
}
