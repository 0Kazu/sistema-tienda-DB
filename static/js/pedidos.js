document.addEventListener('DOMContentLoaded', () => {
    const btnPagar = document.getElementById('btnPagar');

    if (btnPagar) {
        btnPagar.addEventListener('click', async (e) => {
            const idPedido = e.target.getAttribute('data-id');
            
            if(!confirm("¿Estás seguro de procesar el pago? Esto descontará el stock definitivamente.")) return;

            // Deshabilitar botón para evitar doble clic
            btnPagar.disabled = true;
            btnPagar.innerText = "Procesando transaccion...";

            try {
                const response = await fetch(`/pedidos/${idPedido}/pagar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message);
                    window.location.reload(); // Recargar para ver el estado "Pagado"
                } else {
                    // AQUÍ ATRAPAMOS EL SIGNAL DE TU PROCEDIMIENTO ALMACENADO (EJ: Falta de stock)
                    alert("⚠️ ALERTA DE BASE DE DATOS:\n" + data.message);
                    btnPagar.disabled = false;
                    btnPagar.innerText = "💰 Pagar y Facturar";
                }
            } catch (error) {
                alert("Error de conexión con el servidor.");
                btnPagar.disabled = false;
            }
        });
    }
});