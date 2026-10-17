# 🤝 Vyapar Sathi AI - Pure Python Backend (Hackathon Edition)

A high-speed, zero-friction, **100% Pure Python** business management suite for Indian retail, kirana shops, and small businesses. **Zero Node.js dependency.**

---

## ⚡ Hackathon Quickstart (Runs in 1 Second)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Packages: `flask`, `flask-cors`, `pymysql`)*

### 2. Start the Server
Double-click `run.bat` or run:
```bash
python app.py
```

### 3. Open in Browser
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🗄️ Database Options

### Option A: Instant Hackathon Mode (Zero Setup)
By default, the server uses the built-in SQLite engine (`vyapar_sathi.db`). It automatically creates all tables and seeds sample data upon starting. **Requires zero database installation or password configuration.**

### Option B: MySQL Mode
If you want to demonstrate MySQL connectivity to hackathon judges:
1. Update credentials in `.env` (or set environment variables):
   ```env
   DB_TYPE=mysql
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=vyapar_sathi
   ```
2. Run `python app.py`. It connects to MySQL directly via PyMySQL!

---

## 🌟 Hackathon Key Features

1. **⚡ All-in-One Command Center**: Real-time sales, net profit, low-stock warnings, and pending udhaar on a single screen.
2. **🧾 Smart POS Checkout & Auto-Stock Deduction**: Invoicing decrements inventory and logs sales in an atomic database transaction.
3. **🩺 Real-Time AI Business Health Score (0-100)**: Live scoring of store performance.
4. **📋 Day-End Closure (Z-Report)**: 1-click cash drawer reconciliation (Cash vs UPI vs Expenses).
5. **💬 1-Click WhatsApp Khata Reminders**: Instant personalized payment reminders for customers.
6. **📸 OCR Receipt Scanner**: Extract item details from paper bills.
