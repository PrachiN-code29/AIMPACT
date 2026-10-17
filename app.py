import os
import json
import datetime
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Try importing pymysql for MySQL support
try:
    import pymysql
    import pymysql.cursors
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

app = Flask(__name__, static_folder="public")
CORS(app)

# Database Configuration
DB_TYPE = os.environ.get("DB_TYPE", "auto")  # 'mysql', 'sqlite', or 'auto'
MYSQL_HOST = os.environ.get("DB_HOST", "localhost")
MYSQL_USER = os.environ.get("DB_USER", "root")
MYSQL_PASS = os.environ.get("DB_PASSWORD", "")
MYSQL_NAME = os.environ.get("DB_NAME", "vyapar_sathi")
MYSQL_PORT = int(os.environ.get("DB_PORT", 3306))

SQLITE_PATH = "vyapar_sathi.db"

def get_connection():
    """
    Connects to MySQL if available; otherwise effortlessly falls back to SQLite.
    Guarantees that your Hackathon demo never crashes!
    """
    if DB_TYPE != "sqlite" and HAS_PYMYSQL and MYSQL_PASS != "":
        try:
            conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASS,
                database=MYSQL_NAME,
                port=MYSQL_PORT,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return conn, "mysql"
        except Exception:
            pass  # Fall back to SQLite

    # SQLite connection with dict-like row factory
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"

def init_db():
    """Initializes tables and seeds initial data if empty"""
    conn, engine = get_connection()
    cur = conn.cursor()

    if engine == "mysql":
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                qty INT NOT NULL DEFAULT 0,
                cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                low_limit INT NOT NULL DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                type VARCHAR(20) NOT NULL,
                name VARCHAR(255) NOT NULL,
                amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                profit DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                payment_mode VARCHAR(50) DEFAULT 'Cash',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS credits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(255) NOT NULL,
                phone VARCHAR(20) DEFAULT '',
                amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                due_date DATE NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS competitors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NULL,
                product_name VARCHAR(255) NOT NULL,
                competitor_name VARCHAR(255) NOT NULL,
                competitor_price DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                phone VARCHAR(20) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                shop_name VARCHAR(255) DEFAULT 'My Kirana Store',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("SELECT COUNT(*) AS cnt FROM products")
        if cur.fetchone()["cnt"] == 0:
            seed_data(cur, engine)
    else:
        # SQLite
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                qty INTEGER NOT NULL DEFAULT 0,
                cost REAL NOT NULL DEFAULT 0.0,
                price REAL NOT NULL DEFAULT 0.0,
                low_limit INTEGER NOT NULL DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0.0,
                profit REAL NOT NULL DEFAULT 0.0,
                payment_mode TEXT DEFAULT 'Cash',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS credits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                amount REAL NOT NULL DEFAULT 0.0,
                due_date TEXT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS competitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                competitor_name TEXT NOT NULL,
                competitor_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                shop_name TEXT DEFAULT 'My Kirana Store',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] == 0:
            seed_data(cur, engine)
            conn.commit()

    conn.close()

def seed_data(cur, engine):
    items = [
        ("Rice (Basmati 1kg)", 25, 40.0, 52.0, 5),
        ("Wheat Flour (Atta 5kg)", 15, 140.0, 175.0, 5),
        ("Cooking Oil (1L)", 4, 110.0, 135.0, 6),
        ("Sugar (1kg)", 20, 36.0, 44.0, 5),
        ("Tea Dust (250g)", 3, 75.0, 95.0, 5)
    ]
    today = datetime.date.today().isoformat()
    if engine == "mysql":
        for i in items:
            cur.execute("INSERT INTO products (name, qty, cost, price, low_limit) VALUES (%s, %s, %s, %s, %s)", i)
        cur.execute("INSERT INTO transactions (date, type, name, amount, profit, payment_mode) VALUES (%s, 'Sale', 'Rice (Basmati 1kg) × 2', 104.0, 24.0, 'Cash')", (today,))
        cur.execute("INSERT INTO credits (customer_name, phone, amount, due_date, status) VALUES ('Ramesh Sharma', '9876543210', 350.0, %s, 'Pending')", (today,))
    else:
        cur.executemany("INSERT INTO products (name, qty, cost, price, low_limit) VALUES (?, ?, ?, ?, ?)", items)
        cur.execute("INSERT INTO transactions (date, type, name, amount, profit, payment_mode) VALUES (?, 'Sale', 'Rice (Basmati 1kg) × 2', 104.0, 24.0, 'Cash')", (today,))
        cur.execute("INSERT INTO credits (customer_name, phone, amount, due_date, status) VALUES ('Ramesh Sharma', '9876543210', 350.0, ?, 'Pending')", (today,))

def rows_to_list(rows):
    return [dict(r) for r in rows]

# ================= REST API ROUTES =================

@app.route("/")
def index():
    return send_from_directory("public", "index.html")

@app.route("/api/status")
def status():
    conn, engine = get_connection()
    conn.close()
    return jsonify({
        "mysqlConnected": (engine == "mysql"),
        "databaseEngine": engine.upper(),
        "database": MYSQL_NAME if engine == "mysql" else "vyapar_sathi.db",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route("/api/stats")
def stats():
    conn, engine = get_connection()
    cur = conn.cursor()
    today = datetime.date.today().isoformat()

    cur.execute("SELECT * FROM products")
    products = rows_to_list(cur.fetchall())

    cur.execute("SELECT * FROM transactions")
    transactions = rows_to_list(cur.fetchall())

    cur.execute("SELECT * FROM credits")
    credits = rows_to_list(cur.fetchall())
    conn.close()

    today_sales = sum(float(t["amount"]) for t in transactions if t["type"] == "Sale" and str(t["date"]).startswith(today))
    total_sales = sum(float(t["amount"]) for t in transactions if t["type"] == "Sale")
    total_expenses = sum(float(t["amount"]) for t in transactions if t["type"] == "Expense")
    gross_profit = sum(float(t["profit"]) for t in transactions if t["type"] == "Sale")
    net_profit = gross_profit - total_expenses

    inventory_val = sum(float(p["qty"]) * float(p["cost"]) for p in products)
    low_stock = [p for p in products if float(p["qty"]) <= float(p["low_limit"])]

    pending_credits = [c for c in credits if c["status"] != "Paid"]
    total_pending = sum(float(c["amount"]) for c in pending_credits)

    # Health score algorithm (0-100)
    score = 70
    if net_profit > 0: score += 15
    if net_profit < 0: score -= 25
    if len(low_stock) == 0: score += 10
    elif len(low_stock) > 3: score -= 10
    if total_sales > 0 and (total_pending / total_sales) > 0.4: score -= 15
    score = max(10, min(100, score))

    health_status = "Healthy" if score >= 75 else ("Stable" if score >= 50 else "Attention Needed")

    return jsonify({
        "todaySales": today_sales,
        "totalSales": total_sales,
        "totalExpenses": total_expenses,
        "netProfit": net_profit,
        "inventoryValue": inventory_val,
        "totalProducts": len(products),
        "lowStockCount": len(low_stock),
        "pendingUdhaar": total_pending,
        "pendingUdhaarCount": len(pending_credits),
        "healthScore": score,
        "healthStatus": health_status
    })

# --- PRODUCTS CRUD ---
@app.route("/api/products", methods=["GET", "POST"])
def handle_products():
    conn, engine = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        data = request.json or {}
        name = data.get("name", "").strip()
        qty = int(data.get("qty", 0))
        cost = float(data.get("cost", 0.0))
        price = float(data.get("price", 0.0))
        low_limit = int(data.get("low_limit", 5))

        if engine == "mysql":
            cur.execute("INSERT INTO products (name, qty, cost, price, low_limit) VALUES (%s, %s, %s, %s, %s)",
                        (name, qty, cost, price, low_limit))
            new_id = cur.lastrowid
        else:
            cur.execute("INSERT INTO products (name, qty, cost, price, low_limit) VALUES (?, ?, ?, ?, ?)",
                        (name, qty, cost, price, low_limit))
            conn.commit()
            new_id = cur.lastrowid

        conn.close()
        return jsonify({"id": new_id, "name": name, "qty": qty, "cost": cost, "price": price, "low_limit": low_limit})

    cur.execute("SELECT * FROM products ORDER BY name ASC")
    items = rows_to_list(cur.fetchall())
    conn.close()
    return jsonify(items)

@app.route("/api/products/<int:prod_id>", methods=["PUT", "DELETE"])
def product_detail(prod_id):
    conn, engine = get_connection()
    cur = conn.cursor()

    if request.method == "DELETE":
        if engine == "mysql":
            cur.execute("DELETE FROM products WHERE id = %s", (prod_id,))
        else:
            cur.execute("DELETE FROM products WHERE id = ?", (prod_id,))
            conn.commit()
        conn.close()
        return jsonify({"success": True})

    data = request.json or {}
    name = data.get("name")
    qty = int(data.get("qty", 0))
    cost = float(data.get("cost", 0.0))
    price = float(data.get("price", 0.0))
    low_limit = int(data.get("low_limit", 5))

    if engine == "mysql":
        cur.execute("UPDATE products SET name=%s, qty=%s, cost=%s, price=%s, low_limit=%s WHERE id=%s",
                    (name, qty, cost, price, low_limit, prod_id))
    else:
        cur.execute("UPDATE products SET name=?, qty=?, cost=?, price=?, low_limit=? WHERE id=?",
                    (name, qty, cost, price, low_limit, prod_id))
        conn.commit()

    conn.close()
    return jsonify({"success": True, "id": prod_id})

# --- TRANSACTIONS & POS ---
@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    conn, engine = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 50")
    tx = rows_to_list(cur.fetchall())
    conn.close()
    return jsonify(tx)

@app.route("/api/transactions/sale", methods=["POST"])
def quick_sale():
    data = request.json or {}
    product_id = int(data.get("productId", 0))
    qty = int(data.get("qty", 1))
    mode = data.get("paymentMode", "Cash")

    conn, engine = get_connection()
    cur = conn.cursor()

    if engine == "mysql":
        cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    else:
        cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))

    prod = cur.fetchone()
    if not prod:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    prod = dict(prod)
    amount = float(prod["price"]) * qty
    profit = (float(prod["price"]) - float(prod["cost"])) * qty
    today = datetime.date.today().isoformat()

    if engine == "mysql":
        cur.execute("UPDATE products SET qty = GREATEST(0, qty - %s) WHERE id = %s", (qty, product_id))
        cur.execute("INSERT INTO transactions (date, type, name, amount, profit, payment_mode) VALUES (%s, 'Sale', %s, %s, %s, %s)",
                    (today, f"{prod['name']} × {qty}", amount, profit, mode))
        new_id = cur.lastrowid
    else:
        cur.execute("UPDATE products SET qty = MAX(0, qty - ?) WHERE id = ?", (qty, product_id))
        cur.execute("INSERT INTO transactions (date, type, name, amount, profit, payment_mode) VALUES (?, 'Sale', ?, ?, ?, ?)",
                    (today, f"{prod['name']} × {qty}", amount, profit, mode))
        conn.commit()
        new_id = cur.lastrowid

    conn.close()
    return jsonify({"success": True, "transactionId": new_id, "amount": amount, "profit": profit})

@app.route("/api/transactions/expense", methods=["POST"])
def add_expense():
    data = request.json or {}
    name = data.get("name", "").strip()
    amount = float(data.get("amount", 0.0))
    mode = data.get("paymentMode", "Cash")
    today = datetime.date.today().isoformat()

    conn, engine = get_connection()
    cur = conn.cursor()

    if engine == "mysql":
        cur.execute("INSERT INTO transactions (date, type, name, amount, profit, payment_mode) VALUES (%s, 'Expense', %s, %s, %s, %s)",
                    (today, name, amount, -amount, mode))
        new_id = cur.lastrowid
    else:
        cur.execute("INSERT INTO transactions (date, type, name, amount, profit, payment_mode) VALUES (?, 'Expense', ?, ?, ?, ?)",
                    (today, name, amount, -amount, mode))
        conn.commit()
        new_id = cur.lastrowid

    conn.close()
    return jsonify({"success": True, "id": new_id})

# --- POS CART CHECKOUT (Auto Stock Decrement + Khata Integration) ---
@app.route("/api/pos/checkout", methods=["POST"])
def pos_checkout():
    data = request.json or {}
    items = data.get("items", [])
    cust_name = data.get("customerName", "Walk-in Customer")
    phone = data.get("phone", "")
    mode = data.get("paymentMode", "Cash")
    discount = float(data.get("discount", 0.0))
    tax_percent = float(data.get("taxPercent", 0.0))

    if not items:
        return jsonify({"error": "Empty cart"}), 400

    invoice_no = f"INV-{int(datetime.datetime.now().timestamp() * 1000) % 1000000:06d}"
    subtotal = sum(float(i.get("price", 0)) * int(i.get("qty", 1)) for i in items)
    total_profit = sum((float(i.get("price", 0)) - float(i.get("cost", 0))) * int(i.get("qty", 1)) for i in items)
    tax_amount = (subtotal * tax_percent) / 100.0
    final_amount = max(0.0, subtotal + tax_amount - discount)
    today = datetime.date.today().isoformat()

    conn, engine = get_connection()
    cur = conn.cursor()

    # Deduct stock for all items
    for item in items:
        pid = item.get("productId")
        qty = int(item.get("qty", 1))
        if pid:
            if engine == "mysql":
                cur.execute("UPDATE products SET qty = GREATEST(0, qty - %s) WHERE id = %s", (qty, pid))
            else:
                cur.execute("UPDATE products SET qty = MAX(0, qty - ?) WHERE id = ?", (qty, pid))

    # Log sale transaction
    summary = f"Bill {invoice_no}: " + ", ".join(f"{i['name']} × {i['qty']}" for i in items)[:200]
    if engine == "mysql":
        cur.execute("INSERT INTO transactions (date, type, name, amount, profit, payment_mode) VALUES (%s, 'Sale', %s, %s, %s, %s)",
                    (today, summary, final_amount, total_profit - discount, mode))
    else:
        cur.execute("INSERT INTO transactions (date, type, name, amount, profit, payment_mode) VALUES (?, 'Sale', ?, ?, ?, ?)",
                    (today, summary, final_amount, total_profit - discount, mode))

    # Auto-add to Udhaar if payment mode is credit
    if mode == "Udhaar" and cust_name:
        due = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
        if engine == "mysql":
            cur.execute("INSERT INTO credits (customer_name, phone, amount, due_date, status) VALUES (%s, %s, %s, %s, 'Pending')",
                        (cust_name, phone, final_amount, due))
        else:
            cur.execute("INSERT INTO credits (customer_name, phone, amount, due_date, status) VALUES (?, ?, ?, ?, 'Pending')",
                        (cust_name, phone, final_amount, due))

    if engine == "sqlite":
        conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "invoiceNo": invoice_no,
        "subtotal": subtotal,
        "taxAmount": tax_amount,
        "discount": discount,
        "totalAmount": final_amount,
        "itemsCount": len(items)
    })

# --- KHATA / UDHAAR ---
@app.route("/api/credits", methods=["GET", "POST"])
def handle_credits():
    conn, engine = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        data = request.json or {}
        name = data.get("customerName", "").strip()
        phone = data.get("phone", "").strip()
        amount = float(data.get("amount", 0.0))
        due_date = data.get("dueDate")

        if engine == "mysql":
            cur.execute("INSERT INTO credits (customer_name, phone, amount, due_date, status) VALUES (%s, %s, %s, %s, 'Pending')",
                        (name, phone, amount, due_date))
            new_id = cur.lastrowid
        else:
            cur.execute("INSERT INTO credits (customer_name, phone, amount, due_date, status) VALUES (?, ?, ?, ?, 'Pending')",
                        (name, phone, amount, due_date))
            conn.commit()
            new_id = cur.lastrowid

        conn.close()
        return jsonify({"id": new_id, "customer_name": name, "amount": amount, "status": "Pending"})

    cur.execute("SELECT * FROM credits ORDER BY status ASC, id DESC")
    credits = rows_to_list(cur.fetchall())
    conn.close()
    return jsonify(credits)

@app.route("/api/credits/<int:credit_id>/settle", methods=["PUT"])
def settle_credit(credit_id):
    conn, engine = get_connection()
    cur = conn.cursor()
    if engine == "mysql":
        cur.execute("UPDATE credits SET status = 'Paid' WHERE id = %s", (credit_id,))
    else:
        cur.execute("UPDATE credits SET status = 'Paid' WHERE id = ?", (credit_id,))
        conn.commit()
    conn.close()
    return jsonify({"success": True, "id": credit_id, "status": "Paid"})

@app.route("/api/credits/<int:credit_id>", methods=["DELETE"])
def delete_credit(credit_id):
    conn, engine = get_connection()
    cur = conn.cursor()
    if engine == "mysql":
        cur.execute("DELETE FROM credits WHERE id = %s", (credit_id,))
    else:
        cur.execute("DELETE FROM credits WHERE id = ?", (credit_id,))
        conn.commit()
    conn.close()
    return jsonify({"success": True})

# --- COMPETITOR MONITORING ---
@app.route("/api/competitors", methods=["GET", "POST"])
def handle_competitors():
    conn, engine = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        data = request.json or {}
        pid = data.get("productId")
        pname = data.get("productName", "").strip()
        cname = data.get("competitorName", "").strip()
        cprice = float(data.get("competitorPrice", 0.0))

        if engine == "mysql":
            cur.execute("INSERT INTO competitors (product_id, product_name, competitor_name, competitor_price) VALUES (%s, %s, %s, %s)",
                        (pid, pname, cname, cprice))
            new_id = cur.lastrowid
        else:
            cur.execute("INSERT INTO competitors (product_id, product_name, competitor_name, competitor_price) VALUES (?, ?, ?, ?)",
                        (pid, pname, cname, cprice))
            conn.commit()
            new_id = cur.lastrowid

        conn.close()
        return jsonify({"id": new_id, "product_name": pname, "competitor_name": cname, "competitor_price": cprice})

    cur.execute("SELECT * FROM competitors ORDER BY id DESC")
    comp = rows_to_list(cur.fetchall())
    conn.close()
    return jsonify(comp)

# --- DAY-END CLOSURE (Z-REPORT) ---
@app.route("/api/reports/day-end")
def day_end_report():
    today = datetime.date.today().isoformat()
    conn, engine = get_connection()
    cur = conn.cursor()

    if engine == "mysql":
        cur.execute("SELECT * FROM transactions WHERE date = %s", (today,))
    else:
        cur.execute("SELECT * FROM transactions WHERE date = ?", (today,))

    tx = rows_to_list(cur.fetchall())
    conn.close()

    sales = [t for t in tx if t["type"] == "Sale"]
    expenses = [t for t in tx if t["type"] == "Expense"]

    cash_sales = sum(float(s["amount"]) for s in sales if s.get("payment_mode", "Cash") == "Cash")
    upi_sales = sum(float(s["amount"]) for s in sales if s.get("payment_mode") == "UPI")
    udhaar_sales = sum(float(s["amount"]) for s in sales if s.get("payment_mode") == "Udhaar")
    total_sales = sum(float(s["amount"]) for s in sales)
    total_exp = sum(float(e["amount"]) for e in expenses)

    return jsonify({
        "date": today,
        "salesCount": len(sales),
        "totalSales": total_sales,
        "totalCashSales": cash_sales,
        "totalUpiSales": upi_sales,
        "totalUdhaarSales": udhaar_sales,
        "totalExpenses": total_exp,
        "netCashInHand": cash_sales - total_exp,
        "estimatedProfit": sum(float(s["profit"]) for s in sales) - total_exp
    })

# --- AI ADVISOR ---
@app.route("/api/ai/advisor", methods=["POST"])
def ai_advisor():
    data = request.json or {}
    q = data.get("question", "").lower()
    lang = data.get("language", "en")

    conn, engine = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = rows_to_list(cur.fetchall())
    cur.execute("SELECT * FROM transactions WHERE type='Sale'")
    sales = rows_to_list(cur.fetchall())
    conn.close()

    low_stock = [p for p in products if float(p["qty"]) <= float(p["low_limit"])]
    total_rev = sum(float(s["amount"]) for s in sales)

    if "stock" in q or "inventory" in q or "स्टॉक" in q:
        if low_stock:
            ans = f"🚨 Restock Alert: {len(low_stock)} items are below safety limit: {', '.join(p['name'] for p in low_stock)}. Restock soon to prevent missed sales."
        else:
            ans = f"✅ Stock status is healthy! All {len(products)} products have sufficient inventory."
    elif "profit" in q or "margin" in q or "नफा" in q or "कमाई" in q:
        ans = f"💼 Profit Insight: Total recorded revenue is ₹{total_rev:,.2f}. Boost margins by bundling high-margin items (>25%) with fast-moving staples."
    elif "udhaar" in q or "credit" in q or "उधार" in q:
        ans = "👥 Credit Tip: Send polite WhatsApp reminders 1 day prior to due date. Keep credit turnaround under 7 days to preserve working capital."
    else:
        ans = f"💡 Business Diagnosis: Managing {len(products)} active SKUs with ₹{total_rev:,.2f} recorded sales. Maintain inventory levels on top sellers and review slow-moving stock weekly."

    if lang == "hi":
        ans = "व्यापार सलाहकार विश्लेषण:\n" + ans
    elif lang == "mr":
        ans = "व्यवसाय सल्लागार विश्लेषण:\n" + ans

# --- MARKET & COMPETITOR BENCHMARK SEARCH ---
@app.route("/api/market-benchmark")
def market_benchmark():
    prod = request.args.get("product", "").strip()
    market_db = {
        "rice": {"avg_price": 54.0, "range": "₹48 - ₹62 / kg", "sources": ["JioMart", "Blinkit", "Local Mandi"]},
        "wheat": {"avg_price": 180.0, "range": "₹165 - ₹195 / 5kg", "sources": ["Aashirvaad", "DMart", "Zepto"]},
        "oil": {"avg_price": 140.0, "range": "₹130 - ₹155 / L", "sources": ["Fortune", "Blinkit", "BigBasket"]},
        "sugar": {"avg_price": 45.0, "range": "₹42 - ₹48 / kg", "sources": ["Madhur", "Reliance Smart", "JioMart"]},
        "tea": {"avg_price": 95.0, "range": "₹85 - ₹110 / 250g", "sources": ["Red Label", "Tata Tea", "Zepto"]},
        "dal": {"avg_price": 160.0, "range": "₹145 - ₹175 / kg", "sources": ["Toor Dal Super", "DMart Ready"]},
        "milk": {"avg_price": 33.0, "range": "₹32 - ₹35 / 500ml", "sources": ["Amul", "Mother Dairy"]}
    }

    key = prod.lower()
    matched = None
    for k, v in market_db.items():
        if k in key or key in k:
            matched = dict(v)
            matched["matched_item"] = k.capitalize()
            break

    if not matched:
        matched = {
            "avg_price": 60.0,
            "range": "Market dynamic estimate",
            "sources": ["Google Shopping Index", "Local Kirana Average"],
            "matched_item": prod or "General Commodity"
        }

    search_query = f"{prod} price online india blinkit zepto dmart"
    google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

    return jsonify({
        "product": prod,
        "benchmark": matched,
        "google_search_url": google_url
    })

@app.route("/<path:filename>")
def serve_static(filename):
    if os.path.exists(os.path.join("public", filename)):
        return send_from_directory("public", filename)
    return send_from_directory("public", "index.html")

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Vyapar Sathi AI (Python Edition) running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
