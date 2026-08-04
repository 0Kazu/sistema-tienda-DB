USE gestor_tienda_db;

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


-- Otros SP
-- PROCEDIMIENTO PARA CREAR UN PEDIDO
DELIMITER //
DROP PROCEDURE IF EXISTS sp_crear_pedido //
CREATE PROCEDURE sp_crear_pedido(
    IN p_id_cliente INT, 
    IN p_id_usuario INT, 
    IN p_id_metodo INT, 
    OUT p_id_pedido INT
)
BEGIN
    INSERT INTO Pedido (id_cliente, id_usuario, id_metodo_pago, estado, total)
    VALUES (p_id_cliente, p_id_usuario, p_id_metodo, 'Pendiente', 0);
    
    SET p_id_pedido = LAST_INSERT_ID();
END //
DELIMITER ;


-- PROCEDIMIENTO PARA AGREGAR PRODUCTOS (Mueve la lógica de Python a SQL)
DELIMITER //
DROP PROCEDURE IF EXISTS sp_agregar_detalle //
CREATE PROCEDURE sp_agregar_detalle(
    IN p_id_pedido INT, 
    IN p_id_producto INT, 
    IN p_cantidad INT
)
BEGIN
    DECLARE v_precio DECIMAL(10,2);
    DECLARE v_existe INT;

    -- Obtener el precio actual del producto
    SELECT precio_venta INTO v_precio FROM Producto WHERE id_producto = p_id_producto;

    -- Verificar si el producto ya está en el carrito
    SELECT COUNT(*) INTO v_existe FROM Detalle_Pedido 
    WHERE id_pedido = p_id_pedido AND id_producto = p_id_producto;

    IF v_existe > 0 THEN
        UPDATE Detalle_Pedido SET cantidad = cantidad + p_cantidad 
        WHERE id_pedido = p_id_pedido AND id_producto = p_id_producto;
    ELSE
        INSERT INTO Detalle_Pedido (id_pedido, id_producto, cantidad, precio_unitario) 
        VALUES (p_id_pedido, p_id_producto, p_cantidad, v_precio);
    END IF;

    -- Actualizar el total del pedido
    UPDATE Pedido SET total = COALESCE(total, 0) + (p_cantidad * v_precio) 
    WHERE id_pedido = p_id_pedido;
END //
DELIMITER ;


-- PROCEDIMIENTO PARA ELIMINAR PRODUCTOS DEL CARRITO
DELIMITER //
DROP PROCEDURE IF EXISTS sp_eliminar_detalle //
CREATE PROCEDURE sp_eliminar_detalle(
    IN p_id_pedido INT, 
    IN p_id_producto INT
)
BEGIN
    DECLARE v_subtotal DECIMAL(10,2);

    -- Obtener el subtotal de ese producto para restarlo
    SELECT (cantidad * precio_unitario) INTO v_subtotal 
    FROM Detalle_Pedido 
    WHERE id_pedido = p_id_pedido AND id_producto = p_id_producto;

    -- Eliminar la fila
    DELETE FROM Detalle_Pedido 
    WHERE id_pedido = p_id_pedido AND id_producto = p_id_producto;

    -- Restar el valor del total del pedido
    UPDATE Pedido SET total = total - v_subtotal 
    WHERE id_pedido = p_id_pedido;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS sp_eliminar_pedido //
CREATE PROCEDURE sp_eliminar_pedido(
    IN p_id_pedido INT
)
BEGIN
    -- 1. Borramos primero los productos asociados al pedido (por la Integridad Referencial)
    DELETE FROM Detalle_Pedido WHERE id_pedido = p_id_pedido;
    
    -- 2. Borramos la cabecera del pedido
    DELETE FROM Pedido WHERE id_pedido = p_id_pedido;
END //
DELIMITER ;

DELIMITER //

-- SP para listar pedidos según el ROL (Tu regla de negocio)
DROP PROCEDURE IF EXISTS sp_listar_pedidos //
CREATE PROCEDURE sp_listar_pedidos(IN p_rol VARCHAR(50), IN p_id_usuario INT)
BEGIN
    IF p_rol = 'Administrador' THEN
        -- El Admin ve absolutamente todo
        SELECT * FROM vw_historial_pedidos ORDER BY fecha DESC;
    ELSE
        -- El Vendedor solo ve los suyos
        SELECT * FROM vw_historial_pedidos WHERE id_usuario = p_id_usuario ORDER BY fecha DESC;
    END IF;
END //

-- SP para crear Categorías
DROP PROCEDURE IF EXISTS sp_crear_categoria //
CREATE PROCEDURE sp_crear_categoria(IN p_nombre VARCHAR(100), IN p_descripcion TEXT)
BEGIN
    INSERT INTO Categoria (nombre, descripcion) VALUES (p_nombre, p_descripcion);
END //

-- SP para crear Usuarios
DROP PROCEDURE IF EXISTS sp_crear_usuario //
CREATE PROCEDURE sp_crear_usuario(
    IN p_nombre VARCHAR(100), 
    IN p_correo VARCHAR(100), 
    IN p_contrasena VARCHAR(255), 
    IN p_rol VARCHAR(50)
)
BEGIN
    INSERT INTO Usuario (nombre, correo, contrasena, rol, estado) 
    VALUES (p_nombre, p_correo, p_contrasena, p_rol, 'Activo');
END //

DELIMITER ;

DELIMITER //

-- SP para crear un nuevo cliente
DROP PROCEDURE IF EXISTS sp_crear_cliente //
CREATE PROCEDURE sp_crear_cliente(
    IN p_identificacion VARCHAR(20),
    IN p_nombre VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_id_usuario INT
)
BEGIN
    INSERT INTO Cliente (identificacion, nombre, telefono, id_usuario, estado)
    VALUES (p_identificacion, p_nombre, p_telefono, p_id_usuario, 'Activo');
END //

-- SP para actualizar un cliente existente
DROP PROCEDURE IF EXISTS sp_actualizar_cliente //
CREATE PROCEDURE sp_actualizar_cliente(
    IN p_id_cliente INT,
    IN p_identificacion VARCHAR(20),
    IN p_nombre VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_estado ENUM('Activo', 'Inactivo')
)
BEGIN
    UPDATE Cliente
    SET identificacion = p_identificacion,
        nombre = p_nombre,
        telefono = p_telefono,
        estado = p_estado
    WHERE id_cliente = p_id_cliente;
END //

DELIMITER ;

