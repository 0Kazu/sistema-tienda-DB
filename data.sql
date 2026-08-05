USE gestor_tienda_db;

-- ==========================================
-- 1. USUARIOS (Personal de la tienda)
-- ==========================================
INSERT INTO Usuario (nombre, correo, contrasena, rol, estado) VALUES 
('Diego Tello', 'admin@tiendatech.ec', 'scrypt:32768:8:1$randomhash', 'Administrador', 'Activo'),
('Emiliano Tello', 'ventas@tiendatech.ec', 'scrypt:32768:8:1$randomhash', 'Vendedor', 'Activo'),
('Carlos Administrador', 'auditoria@tiendatech.ec', 'scrypt:32768:8:1$randomhash', 'Administrador', 'Inactivo');

-- ==========================================
-- 2. CATEGORÍAS
-- ==========================================
INSERT INTO Categoria (nombre, descripcion) VALUES 
('Componentes PC', 'Tarjetas gráficas, procesadores y placas base'),
('Periféricos', 'Monitores, teclados mecánicos y audífonos'),
('Desarrollo y Software', 'Licencias, sistemas operativos y activos para motores gráficos');

-- ==========================================
-- 3. PROVEEDORES
-- ==========================================
INSERT INTO Proveedor (nombre, contacto, estado) VALUES 
('Tech Import Ecuador', 'ventas@techimport.ec', 'Activo'),
('HP Distribution', 'contacto@hp.com.ec', 'Activo'),
('LG Electronics', '0991234567', 'Activo');

-- ==========================================
-- 4. CLIENTES
-- ==========================================
INSERT INTO Cliente (identificacion, nombre, telefono, estado, id_usuario) VALUES 
('9999999999', 'Consumidor Final', '9999999999', 'Activo', 1),
('0912345678', 'Leonhard Euler', '0987654321', 'Activo', 1),
('0987654321', 'Profesor Calificador', '0911122233', 'Activo', 2);

-- ==========================================
-- 5. PRODUCTOS
-- ==========================================
INSERT INTO Producto (nombre, id_categoria, id_proveedor, precio_costo, precio_venta, stock_actual, stock_minimo, estado, id_usuario) VALUES 
('Monitor LG 20MK400H', 2, 3, 90.00, 125.00, 15, 5, 'Activo', 1),
('Audífonos JBL Tune 780NC', 2, 1, 60.00, 95.00, 20, 5, 'Activo', 1),
('Laptop HP Intel i3', 1, 2, 350.00, 499.99, 8, 3, 'Activo', 1),
('Licencia Unity Pro (1 Año)', 3, 1, 1500.00, 1800.00, 5, 2, 'Activo', 1),
('Tarjeta Gráfica GT 1030', 1, 1, 85.00, 110.00, 12, 4, 'Activo', 2),
('Pendrive 64GB (Fedora Linux Bootable)', 3, 1, 15.00, 25.00, 3, 10, 'Activo', 2); -- Este saldrá con alerta de stock bajo

-- ==========================================
-- 6. MÉTODOS DE PAGO
-- ==========================================
INSERT IGNORE INTO Metodo_Pago (id_metodo_pago, nombre, descripcion) VALUES 
(1, 'Efectivo', 'Pago en caja'),
(2, 'Transferencia', 'Pichincha / Guayaquil / Pacífico'),
(3, 'Tarjeta', 'Crédito y Débito');

-- ==========================================
-- 7. PEDIDOS (Para que el dashboard y reportes tengan vida)
-- ==========================================
INSERT INTO Pedido (id_pedido, fecha, estado, total, id_usuario, id_cliente, id_metodo_pago) VALUES 
(1, DATE_SUB(NOW(), INTERVAL 5 DAY), 'Pagado', 220.00, 1, 1, 1),
(2, DATE_SUB(NOW(), INTERVAL 1 DAY), 'Pagado', 110.00, 2, 2, 2),
(3, NOW(), 'Pendiente', 499.99, 2, 3, 3);

-- ==========================================
-- 8. DETALLES DE PEDIDO
-- ==========================================
-- Pedido 1 (Consumidor Final, Pagado en Efectivo)
INSERT INTO Detalle_Pedido (id_pedido, id_producto, cantidad, precio_unitario) VALUES 
(1, 1, 1, 125.00), -- Monitor LG
(1, 2, 1, 95.00);  -- Audífonos JBL

-- Pedido 2 (Leonhard, Pagado por Transferencia)
INSERT INTO Detalle_Pedido (id_pedido, id_producto, cantidad, precio_unitario) VALUES 
(2, 5, 1, 110.00); -- Tarjeta Gráfica

-- Pedido 3 (Profesor, Pendiente de pago)
INSERT INTO Detalle_Pedido (id_pedido, id_producto, cantidad, precio_unitario) VALUES 
(3, 3, 1, 499.99); -- Laptop HP