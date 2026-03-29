-- DATABASE
CREATE DATABASE IF NOT EXISTS WarehouseDB;
USE WarehouseDB;

-- TABLES

CREATE TABLE IF NOT EXISTS Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(50),
    price DECIMAL(10,2),
    category VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Warehouse (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_name VARCHAR(50),
    location VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(50),
    phone VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS Inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    warehouse_id INT,
    quantity INT,
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    inventory_id INT,
    type VARCHAR(10),
    quantity INT,
    date DATE,
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    FOREIGN KEY (inventory_id) REFERENCES Inventory(inventory_id)
);

CREATE TABLE IF NOT EXISTS PurchaseOrders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT,
    product_id INT,
    quantity INT,
    order_date DATE,
    status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

-- SAMPLE DATA

INSERT INTO Products (product_name, price, category) VALUES
('Laptop',50000,'Electronics'),
('Mouse',500,'Electronics'),
('Keyboard',1000,'Electronics');

INSERT INTO Warehouse (warehouse_name, location) VALUES
('Main Warehouse','Chennai'),
('Backup Warehouse','Bangalore');

INSERT INTO Suppliers (supplier_name, phone) VALUES
('ABC Suppliers','9876543210'),
('XYZ Traders','9123456780');

INSERT INTO Inventory (product_id, warehouse_id, quantity) VALUES
(1,1,10),
(2,1,50),
(3,2,30);

INSERT INTO Transactions (product_id, inventory_id, type, quantity, date) VALUES
(1,1,'IN',10,'2025-03-01'),
(2,2,'IN',50,'2025-03-02'),
(3,3,'OUT',5,'2025-03-03');

INSERT INTO PurchaseOrders (supplier_id, product_id, quantity, order_date, status) VALUES
(1,1,20,'2025-03-05','Pending'),
(2,2,40,'2025-03-06','Completed');