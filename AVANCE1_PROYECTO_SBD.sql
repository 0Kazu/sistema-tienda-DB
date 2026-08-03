SET FOREIGN_KEY_CHECKS = 0;

Create Database IF NOT EXISTS gestor_tienda_db;
USE gestor_tienda_db;

-- Inicio SQL
Create Database IF NOT EXISTS gestor_tienda_db;
USE gestor_tienda_db; 
-- TABLA: USUARIO
DROP TABLE IF EXISTS Usuario;
CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol ENUM('Administrador', 'Vendedor', 'Bodeguero') NOT NULL,
    estado ENUM('Activo', 'Inactivo') DEFAULT 'Activo'
);


-- TABLA: CLIENTE
DROP TABLE IF EXISTS Cliente;
CREATE TABLE IF NOT EXISTS Cliente (
    id_cliente INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    identificacion VARCHAR(50),
    telefono VARCHAR(20),
    estado ENUM('Activo', 'Inactivo') DEFAULT 'Activo',
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

-- TABLA: METODO_PAGO
DROP TABLE IF EXISTS Metodo_Pago;
CREATE TABLE IF NOT EXISTS Metodo_Pago (
    id_metodo_pago INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255)
);


-- TABLA: PROVEEDOR
DROP TABLE IF EXISTS Proveedor;
CREATE TABLE IF NOT EXISTS Proveedor (
    id_proveedor INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    estado ENUM('Activo', 'Inactivo') DEFAULT 'Activo'
);


-- TABLA: CATEGORIA
DROP TABLE IF EXISTS Categoria;
CREATE TABLE IF NOT EXISTS Categoria (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255)
);


-- TABLA: PRODUCTO
DROP TABLE IF EXISTS Producto;
CREATE TABLE IF NOT EXISTS Producto (
    id_producto INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    precio_costo DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 0,
    estado ENUM('Activo', 'Inactivo') DEFAULT 'Activo',
    
    id_usuario INT NOT NULL,
    id_proveedor INT NOT NULL,
    id_categoria INT NOT NULL,

    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_proveedor) REFERENCES Proveedor(id_proveedor),
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria),

    CHECK (precio_venta >= precio_costo),
    CHECK (stock_actual >= 0),
    CHECK (stock_minimo >= 0)
);


-- TABLA: PEDIDO
DROP TABLE IF EXISTS Pedido;
CREATE TABLE IF NOT EXISTS Pedido (
    id_pedido INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('Pendiente', 'Pagado', 'Anulado') NOT NULL,
    total DECIMAL(10,2),

    id_usuario INT NOT NULL,
    id_cliente INT NOT NULL,
    id_metodo_pago INT NOT NULL,

    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    FOREIGN KEY (id_metodo_pago) REFERENCES Metodo_Pago(id_metodo_pago)
);


-- TABLA: DETALLE_PEDIDO 
DROP TABLE IF EXISTS Detalle_Pedido;
CREATE TABLE IF NOT EXISTS Detalle_Pedido (
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,

    PRIMARY KEY (id_pedido, id_producto),

    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto),

    CHECK (cantidad > 0)
);


-- TABLA: AJUSTE_INVENTARIO
DROP TABLE IF EXISTS Ajuste_Inventario;
CREATE TABLE IF NOT EXISTS Ajuste_Inventario (
    id_ajuste INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo ENUM('Entrada', 'Salida') NOT NULL,
    cantidad INT NOT NULL,
    descripcion VARCHAR(255),

    id_producto INT NOT NULL,

    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto),
    CHECK (cantidad > 0)
);

-- Procedimiento Pagar Pedido
DELIMITER //
DROP PROCEDURE IF EXISTS sp_pagar_pedido //

CREATE PROCEDURE sp_pagar_pedido(IN p_id_pedido INT)
BEGIN
    DECLARE v_id_producto INT;
    DECLARE v_cantidad INT;
    DECLARE v_stock_actual INT;
    DECLARE done INT DEFAULT FALSE;

    -- Obtener todos los productos dentro del pedido
    DECLARE cur_detalles CURSOR FOR
        SELECT id_producto, cantidad FROM Detalle_Pedido WHERE id_pedido = p_id_pedido;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- INICIO DE LA TRANSACCIÓN
    START TRANSACTION;

    -- Validar que el pedido esté 'Pendiente'.
    IF (SELECT estado FROM Pedido WHERE id_pedido = p_id_pedido FOR UPDATE) != 'Pendiente' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Solo se pueden procesar pedidos en estado Pendiente.';
    END IF;

    OPEN cur_detalles;

    read_loop: LOOP
        FETCH cur_detalles INTO v_id_producto, v_cantidad;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Verificar el stock y bloquear la fila del producto
        SELECT stock_actual INTO v_stock_actual
        FROM Producto WHERE id_producto = v_id_producto FOR UPDATE;

        IF v_stock_actual < v_cantidad THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error de Integridad: Stock insuficiente para procesar la venta.';
        END IF;

        -- Descontar del inventario
        UPDATE Producto
        SET stock_actual = stock_actual - v_cantidad
        WHERE id_producto = v_id_producto;
    END LOOP;

    CLOSE cur_detalles;

    -- Actualizar el estado del pedido a 'Pagado'
    UPDATE Pedido SET estado = 'Pagado' WHERE id_pedido = p_id_pedido;

    COMMIT;
END //
DELIMITER ;

-- Triggers

-- Trigger 1
DROP TRIGGER IF EXISTS tg_ajuste_inventario_after_insert;
DELIMITER //
-- Actualiza el stock automáticamente cada vez que el Bodeguero inserta un Ajuste de Inventario.
CREATE TRIGGER tg_ajuste_inventario_after_insert
    AFTER INSERT ON Ajuste_Inventario
    FOR EACH ROW
BEGIN
    IF NEW.tipo = 'Entrada' THEN
        UPDATE Producto SET stock_actual = stock_actual + NEW.cantidad WHERE id_producto = NEW.id_producto;
    ELSE
        UPDATE Producto SET stock_actual = stock_actual - NEW.cantidad WHERE id_producto = NEW.id_producto;
    END IF;
END //
DELIMITER ;

-- Trigger 2
DROP TRIGGER IF EXISTS tg_prevent_delete_cliente;

-- Evita que se elimine un Cliente si este ya tiene historial de pedidos en el sistema.
DELIMITER //
CREATE TRIGGER tg_prevent_delete_cliente
    BEFORE DELETE ON Cliente
    FOR EACH ROW
BEGIN
    DECLARE total_pedidos INT;
    SELECT COUNT(*) INTO total_pedidos FROM Pedido WHERE id_cliente = OLD.id_cliente;

    IF total_pedidos > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Operación rechazada: El cliente posee historial de pedidos. Debe cambiar su estado a Inactivo.';
    END IF;
END //
DELIMITER ;


-- Trigger 3
DROP TRIGGER IF EXISTS tg_validate_producto_activo;

DELIMITER //
-- Impide que un vendedor agregue al carrito un producto que esté 'Inactivo' en el catálogo
CREATE TRIGGER tg_validate_producto_activo
    BEFORE INSERT ON Detalle_Pedido
    FOR EACH ROW
BEGIN
    DECLARE estado_prod VARCHAR(20);
    SELECT estado INTO estado_prod FROM Producto WHERE id_producto = NEW.id_producto;

    IF estado_prod = 'Inactivo' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Operación rechazada: No se pueden vender productos inactivos.';
    END IF;
END //
DELIMITER ;

-- Trigger 4
DROP TRIGGER IF EXISTS tg_prevent_modificar_pedido;

DELIMITER //
-- Evita que se le agreguen más detalles (productos) a un Pedido que ya fue Pagado o Anulado
CREATE TRIGGER tg_prevent_modificar_pedido
    BEFORE INSERT ON Detalle_Pedido
    FOR EACH ROW
BEGIN
    DECLARE estado_pedido VARCHAR(20);
    SELECT estado INTO estado_pedido FROM Pedido WHERE id_pedido = NEW.id_pedido;

    IF estado_pedido != 'Pendiente' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Operación rechazada: Solo se pueden agregar productos a un pedido Pendiente.';
END IF;
END //
DELIMITER ;

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

-- Final SQL
SET FOREIGN_KEY_CHECKS = 1;