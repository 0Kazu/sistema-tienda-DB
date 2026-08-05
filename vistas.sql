USE gestor_tienda_db;

-- Vistas
-- Vista de productos con bajo stock (Para el Bodeguero y ADMIN)
DROP VIEW IF EXISTS vw_productos_bajo_stock;
CREATE VIEW vw_productos_bajo_stock AS
SELECT
    id_producto,
    nombre,
    stock_actual,
    stock_minimo
FROM Producto
WHERE stock_actual <= stock_minimo AND estado = 'Activo';

-- Vista de historial de Pedidos con nombre del cliente
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

-- Vista de reporte de productos más vendidos
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

-- Vista de auditoría de ajustes de inventario
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

-- Otras vistas igual de relevantes
CREATE OR REPLACE VIEW vw_clientes_activos AS 
SELECT id_cliente, nombre FROM Cliente WHERE estado = 'Activo';

CREATE OR REPLACE VIEW vw_usuarios_activos AS 
SELECT id_usuario, nombre FROM Usuario WHERE estado = 'Activo';

CREATE OR REPLACE VIEW vw_productos_activos AS 
SELECT id_producto, nombre, precio_venta, stock_actual FROM Producto WHERE estado = 'Activo';

-- Vista para listar clientes con el nombre del usuario que los registró
CREATE OR REPLACE VIEW vw_lista_clientes AS
SELECT c.id_cliente, c.nombre, c.identificacion, c.telefono, c.estado,
       u.nombre AS registrado_por
FROM Cliente c
JOIN Usuario u ON c.id_usuario = u.id_usuario
ORDER BY c.id_cliente DESC;

-- Vista para listar productos con sus categorías y proveedores
CREATE OR REPLACE VIEW vw_lista_productos AS
SELECT p.id_producto, p.nombre, c.nombre AS categoria, 
       pr.nombre AS proveedor, p.precio_costo, p.precio_venta, 
       p.stock_actual, p.stock_minimo, p.estado
FROM Producto p
JOIN Categoria c ON p.id_categoria = c.id_categoria
JOIN Proveedor pr ON p.id_proveedor = pr.id_proveedor
ORDER BY p.id_producto DESC;

-- Vistas adicionales para los menús desplegables (formularios)
CREATE OR REPLACE VIEW vw_categorias_activas AS 
SELECT id_categoria, nombre FROM Categoria;

CREATE OR REPLACE VIEW vw_proveedores_activos AS 
SELECT id_proveedor, nombre FROM Proveedor WHERE estado = 'Activo';

-- Vista para el Login
CREATE OR REPLACE VIEW vw_auth_usuarios AS
SELECT id_usuario, nombre, correo, contrasena, rol, estado FROM Usuario;

-- Vista para listar Categorías
CREATE OR REPLACE VIEW vw_lista_categorias AS
SELECT * FROM Categoria ORDER BY id_categoria DESC;

-- Reemplazamos la vista de historial para ASEGURARNOS de que incluya el id_usuario
CREATE OR REPLACE VIEW vw_historial_pedidos AS
SELECT p.id_pedido, p.fecha, c.nombre AS cliente, u.nombre AS vendedor, p.total, p.estado, p.id_usuario
FROM Pedido p
JOIN Cliente c ON p.id_cliente = c.id_cliente
JOIN Usuario u ON p.id_usuario = u.id_usuario;

-- Vista para ver el detalle del pedido
CREATE OR REPLACE VIEW vw_detalles_pedido AS
SELECT 
    dp.id_pedido, 
    dp.id_producto, -- Importante para que tu botón de eliminar sepa qué producto borrar
    p.nombre AS nombre_producto, 
    dp.cantidad, 
    dp.precio_unitario, 
    (dp.cantidad * dp.precio_unitario) AS subtotal -- Cálculo al vuelo
FROM Detalle_Pedido dp
JOIN Producto p ON dp.id_producto = p.id_producto;

-- Vista para ver los Usuarios creados en el sistema (No clientes)
CREATE OR REPLACE VIEW vw_lista_usuarios AS
SELECT id_usuario, nombre, correo, rol, estado
FROM Usuario
ORDER BY id_usuario DESC;

-- Vista segura para listar los proveedores en la sección productos
CREATE OR REPLACE VIEW vw_lista_proveedores AS
SELECT id_proveedor, nombre, contacto, estado
FROM Proveedor
ORDER BY id_proveedor DESC;
