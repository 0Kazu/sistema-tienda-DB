document.addEventListener("DOMContentLoaded", () => {
    initFormularioProducto();
    initBotonesEliminarProducto();
});

function initFormularioProducto() {
    const form = document.getElementById("form-producto");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = {
            nombre: form.nombre.value.trim(),
            precio_costo: form.precio_costo.value,
            precio_venta: form.precio_venta.value,
            stock_actual: form.stock_actual.value,
            stock_minimo: form.stock_minimo.value,
            estado: form.estado.value,
            id_usuario: form.id_usuario.value,
            id_proveedor: form.id_proveedor.value,
            id_categoria: form.id_categoria.value,
        };

        const modo = form.dataset.modo; // "crear" | "editar"
        const url = modo === "editar" ? `/productos/api/${form.dataset.idProducto}` : "/productos/api";
        const method = modo === "editar" ? "PUT" : "POST";

        const submitBtn = form.querySelector("button[type='submit']");
        submitBtn.classList.add("is-loading");

        const data = await apiRequest(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        submitBtn.classList.remove("is-loading");

        if (data) {
            window.location.href = "/productos/";
        }
    });
}

function initBotonesEliminarProducto() {
    document.querySelectorAll(".btn-eliminar-producto").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.id;
            const nombre = btn.dataset.nombre;

            if (!confirm(`¿Eliminar el producto "${nombre}"? Esta acción no se puede deshacer.`)) {
                return;
            }

            const data = await apiRequest(`/productos/api/${id}`, { method: "DELETE" });

            if (data) {
                showAlert("success", data.message);
                const fila = document.getElementById(`producto-${id}`);
                if (fila) fila.remove();
            }
        });
    });
}
