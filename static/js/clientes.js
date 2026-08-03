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

        // apiRequest ya mostró la alerta de error si algo falló.
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
        });
    });
}
