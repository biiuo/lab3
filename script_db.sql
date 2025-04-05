CREATE DATABASE venta;
USE venta;

-- 1. Creación de la tabla Proveedor
CREATE TABLE Proveedor (
    nit VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    direccion VARCHAR(100) NOT NULL
);

-- 2. Creación de la tabla Producto
CREATE TABLE Producto (
    codigo VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    nit_proveedor VARCHAR(20) NOT NULL,
    FOREIGN KEY (nit_proveedor) REFERENCES Proveedor(nit)
);

-- 3. Creación de la tabla Cliente (como la definiste, pero mejorada)
CREATE TABLE Cliente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellidos VARCHAR(50) NOT NULL,
    fecha_nac DATETIME NOT NULL,
    direccion VARCHAR(100) NOT NULL
);

-- 4. Creación de la tabla Compra (para la relación muchos-a-muchos)
CREATE TABLE Compra (
    id_cliente INT,
    codigo_producto VARCHAR(20),
    cantidad INT NOT NULL,
    fecha_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_cliente, codigo_producto, fecha_compra),
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id),
    FOREIGN KEY (codigo_producto) REFERENCES Producto(codigo)
);

-- Inserción de datos de ejemplo

-- Proveedores
INSERT INTO Proveedor (nit, nombre, direccion) VALUES
('123456789', 'Distribuidora Tech', 'Calle 123, Ciudad A'),
('987654321', 'Suministros Express', 'Avenida 456, Ciudad B');

-- Productos
INSERT INTO Producto (codigo, nombre, precio_unitario, nit_proveedor) VALUES
('P100', 'Laptop Elite', 1200.00, '123456789'),
('P200', 'Teclado Mecánico', 85.50, '123456789'),
('P300', 'Mouse Inalámbrico', 25.75, '987654321');

-- Clientes
INSERT INTO Cliente (nombre, apellidos, fecha_nac, direccion) VALUES
('Juan', 'Pérez García', '1990-05-15', 'Calle Falsa 123'),
('María', 'López Martínez', '1985-08-22', 'Avenida Real 456'),
('Carlos', 'Gómez Sánchez', '1995-03-10', 'Boulevard Central 789');

-- Compras
INSERT INTO Compra (id_cliente, codigo_producto, cantidad) VALUES
(1, 'P100', 1),
(1, 'P300', 2),
(2, 'P200', 3),
(3, 'P100', 1),
(3, 'P200', 1),
(3, 'P300', 1);

Alter table compra add total float NOT NULL DEFAULT 0;