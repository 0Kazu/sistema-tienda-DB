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