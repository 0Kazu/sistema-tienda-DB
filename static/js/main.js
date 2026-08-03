/**
 * Helpers compartidos por todas las vistas del proyecto.
 *
 * showAlert() es la pieza clave para el requisito de "atrapar excepciones
 * SQL y mostrarlas como alertas legibles": cuando cualquier módulo (Productos,
 * Clientes, Pedidos) haga un fetch() a Flask y la respuesta tenga
 * success=false, basta con llamar showAlert('danger', data.message) para
 * pintar el mensaje que vino directamente del trigger / procedimiento.
 */

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

/**
 * Wrapper sobre fetch() pensado para las futuras rutas JSON del CRUD.
 * Centraliza el parseo de la respuesta y, si success=false (por ejemplo,
 * un DatabaseError capturado en app.py), muestra la alerta automáticamente.
 *
 * Uso previsto en los próximos pasos:
 *   const data = await apiRequest('/api/productos', { method: 'POST', body: formData });
 *   if (data) { ...actualizar la tabla... }
 */
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
