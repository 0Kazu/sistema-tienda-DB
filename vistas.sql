-- Vistas
-- VISTA 1: Productos con bajo stock (Para el Bodeguero)
DROP VIEW IF EXISTS vw_productos_bajo_stock;
CREATE VIEW vw_productos_bajo_stock AS
SELECT
    id_producto,
    nombre,
    stock_actual,
    stock_minimo
FROM Producto
WHERE stock_actual <= stock_minimo AND estado = 'Activo';

-- VISTA 2: Historial de Pedidos con nombre del cliente
DROP VIEW IF EXISTS vw_historial_pedidos;
CREATE VIEW vw_historial_pedidos AS
SELECT
    p.id_pedido,
    p.fecha,
    c.nombre AS cliente,
    p.estado,
    p.total
FROM Pedido p
JOIN Cliente c ON p.id_cliente = c.id_cliente;

-- VISTA 3: Reporte de productos más vendidos
DROP VIEW IF EXISTS vw_top_productos_vendidos;
CREATE VIEW vw_top_productos_vendidos AS
SELECT
    pr.nombre AS producto,
    SUM(dp.cantidad) AS total_unidades_vendidas,
    SUM(dp.cantidad * dp.precio_unitario) AS ingresos_totales
FROM Detalle_Pedido dp
JOIN Producto pr ON dp.id_producto = pr.id_producto
JOIN Pedido p ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'Pagado'
GROUP BY pr.id_producto, pr.nombre
ORDER BY total_unidades_vendidas DESC;

-- VISTA 4: Auditoría de ajustes de inventario
DROP VIEW IF EXISTS vw_auditoria_inventario;
CREATE VIEW vw_auditoria_inventario AS
SELECT
    a.fecha,
    p.nombre AS producto,
    a.tipo,
    a.cantidad,
    a.descripcion
FROM Ajuste_Inventario a
JOIN Producto p ON a.id_producto = p.id_producto
ORDER BY a.fecha DESC;

-- Otras vistas
CREATE OR REPLACE VIEW vw_clientes_activos AS 
SELECT id_cliente, nombre FROM Cliente WHERE estado = 'Activo';

CREATE OR REPLACE VIEW vw_usuarios_activos AS 
SELECT id_usuario, nombre FROM Usuario WHERE estado = 'Activo';

CREATE OR REPLACE VIEW vw_productos_activos AS 
SELECT id_producto, nombre, precio_venta, stock_actual FROM Producto WHERE estado = 'Activo';

-- Admin por defecto
INSERT INTO Usuario(nombre, correo, contrasena, estado)
VALUES ('Diego', 'admin@tienda.com', '12345', 'Activo')
