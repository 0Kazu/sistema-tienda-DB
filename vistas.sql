USE gestor_tienda_db;

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

USE gestor_tienda_db;

-- 2. Crear Proveedor y Categoría (Obligatorios para Producto)
INSERT INTO Proveedor (nombre, contacto) 
VALUES ('Importadora Tech', '0991234567');

INSERT INTO Categoria (nombre, descripcion) 
VALUES ('Periféricos', 'Teclados, mouses y audífonos');

-- 3. Crear Productos
INSERT INTO Producto (nombre, precio_costo, precio_venta, stock_actual, stock_minimo, id_usuario, id_proveedor, id_categoria)
VALUES 
-- Producto 1: Todo normal (Stock 30, Mínimo 10)
('Mouse Inalámbrico', 10.00, 20.00, 30, 10, 1, 1, 1),

-- Producto 2: ¡STOCK BAJO! (Stock 2, Mínimo 5). Este debería aparecer en tu web.
('Teclado Mecánico', 35.00, 60.00, 2, 5, 1, 1, 1);


INSERT INTO Metodo_Pago (nombre, descripcion) VALUES ('Efectivo', 'Pago en caja'), ('Transferencia', 'Pichincha/Guayaquil');