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

-- Índices
-- Índice vital para el "Dashboard"; acelera el filtro de pedidos pendientes vs pagados
CREATE INDEX idx_pedido_estado ON Pedido(estado);

-- Índice para optimizar el reporte de ventas
CREATE INDEX idx_pedido_fecha ON Pedido(fecha);


