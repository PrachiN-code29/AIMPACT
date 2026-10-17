-- Vyapar Sathi AI - MySQL Database Schema
-- Run this in MySQL Workbench, phpMyAdmin, or MySQL CLI:
-- mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS vyapar_sathi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vyapar_sathi;

-- 1. Products Table
CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  qty INT NOT NULL DEFAULT 0,
  cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  low_limit INT NOT NULL DEFAULT 5,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Transactions Table (Sales, Expenses)
CREATE TABLE IF NOT EXISTS transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE NOT NULL,
  type ENUM('Sale', 'Expense') NOT NULL,
  name VARCHAR(255) NOT NULL,
  amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  profit DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  payment_mode VARCHAR(50) DEFAULT 'Cash',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Customer Udhaar / Credit Tracker Table
CREATE TABLE IF NOT EXISTS credits (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_name VARCHAR(255) NOT NULL,
  phone VARCHAR(20) DEFAULT '',
  amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  due_date DATE NULL,
  status ENUM('Pending', 'Paid') NOT NULL DEFAULT 'Pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  settled_at TIMESTAMP NULL
);

-- 4. Competitor Price Monitoring Table
CREATE TABLE IF NOT EXISTS competitors (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NULL,
  product_name VARCHAR(255) NOT NULL,
  competitor_name VARCHAR(255) NOT NULL,
  competitor_price DECIMAL(10, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- 5. Invoices / Bills Table
CREATE TABLE IF NOT EXISTS bills (
  id INT AUTO_INCREMENT PRIMARY KEY,
  invoice_no VARCHAR(50) NOT NULL UNIQUE,
  customer_name VARCHAR(255) DEFAULT 'Walk-in Customer',
  phone VARCHAR(20) DEFAULT '',
  subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  tax_percent DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
  tax_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  discount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  payment_mode VARCHAR(50) DEFAULT 'Cash',
  items_json JSON NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed Initial Products (if table is empty)
INSERT INTO products (name, qty, cost, price, low_limit)
SELECT 'Rice (Basmati 1kg)', 25, 40.00, 52.00, 5 FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM products LIMIT 1);

INSERT INTO products (name, qty, cost, price, low_limit)
SELECT 'Wheat Flour (Atta 5kg)', 15, 140.00, 175.00, 5 FROM DUAL
WHERE (SELECT COUNT(*) FROM products) = 1;

INSERT INTO products (name, qty, cost, price, low_limit)
SELECT 'Cooking Oil (1L)', 4, 110.00, 135.00, 6 FROM DUAL
WHERE (SELECT COUNT(*) FROM products) = 2;

INSERT INTO products (name, qty, cost, price, low_limit)
SELECT 'Sugar (1kg)', 20, 36.00, 44.00, 5 FROM DUAL
WHERE (SELECT COUNT(*) FROM products) = 3;

INSERT INTO products (name, qty, cost, price, low_limit)
SELECT 'Tea Dust (250g)', 3, 75.00, 95.00, 5 FROM DUAL
WHERE (SELECT COUNT(*) FROM products) = 4;
