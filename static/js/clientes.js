/**
 * Vista Clientes: alta, edición y baja usando las rutas JSON del blueprint
 * routes/clientes.py (POST/PUT/DELETE /clientes/api...).
 *
 * Mismo patrón que static/js/productos.js: el listado y los formularios se
 * sirven como HTML normal desde Flask+Jinja; solo las escrituras pasan por
 * fetch() (vía apiRequest(), definido en main.js) para poder mostrar los
 * errores de la BD -incluido el SIGNAL del trigger tg_prevent_delete_cliente-
 * como alertas de Bootstrap sin recargar la página.
 */

document.addEventListener("DOMContentLoaded", () => {
    initFormularioCliente();
    initBotonesEliminarCliente();
});

function initFormularioCliente() {
    const form = document.getElementById("form-cliente");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = {
            nombre: form.nombre.value.trim(),
            identificacion: form.identificacion.value.trim(),
            telefono: form.telefono.value.trim(),
            estado: form.estado.value,
            id_usuario: form.id_usuario.value,
        };

        const modo = form.dataset.modo; // "crear" | "editar"
        const url = modo === "editar" ? `/clientes/api/${form.dataset.idCliente}` : "/clientes/api";
        const method = modo === "editar" ? "PUT" : "POST";

        const submitBtn = form.querySelector("button[type='submit']");
        submitBtn.classList.add("is-loading");

        const data = await apiRequest(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        submitBtn.classList.remove("is-loading");

        // apiRequest ya mostró la alerta de error si algo falló. Si data
        // existe, la operación tuvo éxito.
        if (data) {
            window.location.href = "/clientes/";
        }
    });
}

function initBotonesEliminarCliente() {
    document.querySelectorAll(".btn-eliminar-cliente").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.id;
            const nombre = btn.dataset.nombre;

            if (!confirm(`¿Eliminar al cliente "${nombre}"? Esta acción no se puede deshacer.`)) {
                return;
            }

            const data = await apiRequest(`/clientes/api/${id}`, { method: "DELETE" });

            if (data) {
                showAlert("success", data.message);
                const fila = document.getElementById(`cliente-${id}`);
                if (fila) fila.remove();
            }
            // Si el cliente tiene pedidos, el trigger tg_prevent_delete_cliente
            // rechaza el DELETE y apiRequest ya mostró esa alerta con el
            // mensaje exacto que definió el trigger (RB07).
        });
    });
}
