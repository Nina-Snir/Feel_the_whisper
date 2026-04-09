import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "feel_the_whisper.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'member',
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            instagram TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            email TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS customer_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            customer_name TEXT NOT NULL,
            products TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Nová',
            notes TEXT,
            order_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS supplier_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER,
            supplier_name TEXT NOT NULL,
            products TEXT NOT NULL,
            quantity INTEGER,
            amount REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Objednaná',
            deadline TEXT,
            notes TEXT,
            order_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            description TEXT,
            related_order_id INTEGER,
            created_by INTEGER,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS finances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            related_order_id INTEGER,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS marketing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            channel TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Plánovaná',
            planned_date TEXT,
            published_date TEXT,
            notes TEXT,
            result TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()

    # Seed admin
    existing = c.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
    if not existing:
        now = datetime.now().isoformat()
        c.execute(
            "INSERT INTO users (username, password, full_name, role, created_at) VALUES (?,?,?,?,?)",
            ("admin", hash_pw("admin123"), "Administrátor", "admin", now)
        )
        conn.commit()

    conn.close()


# ── AUTH ──────────────────────────────────────────────────────────────────────

def login(username: str, password: str):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_pw(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ── USERS ─────────────────────────────────────────────────────────────────────

def get_users():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_user(username, password, full_name, role):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO users (username, password, full_name, role, created_at) VALUES (?,?,?,?,?)",
        (username, hash_pw(password), full_name, role, now)
    )
    conn.commit()
    conn.close()


def delete_user(user_id):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


# ── CUSTOMERS ─────────────────────────────────────────────────────────────────

def get_customers(search=""):
    conn = get_conn()
    if search:
        rows = conn.execute(
            "SELECT * FROM customers WHERE name LIKE ? OR email LIKE ? OR instagram LIKE ? ORDER BY name",
            (f"%{search}%", f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM customers ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_customer(name, email, phone, instagram, notes):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO customers (name, email, phone, instagram, notes, created_at) VALUES (?,?,?,?,?,?)",
        (name, email, phone, instagram, notes, now)
    )
    conn.commit()
    conn.close()


def update_customer(cid, name, email, phone, instagram, notes):
    conn = get_conn()
    conn.execute(
        "UPDATE customers SET name=?, email=?, phone=?, instagram=?, notes=? WHERE id=?",
        (name, email, phone, instagram, notes, cid)
    )
    conn.commit()
    conn.close()


def delete_customer(cid):
    conn = get_conn()
    conn.execute("DELETE FROM customers WHERE id=?", (cid,))
    conn.commit()
    conn.close()


def get_customer_order_history(customer_name):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM customer_orders WHERE customer_name LIKE ? ORDER BY order_date DESC",
        (f"%{customer_name}%",)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── SUPPLIERS ─────────────────────────────────────────────────────────────────

def get_suppliers():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_supplier(name, contact, email, notes):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO suppliers (name, contact, email, notes, created_at) VALUES (?,?,?,?,?)",
        (name, contact, email, notes, now)
    )
    conn.commit()
    conn.close()


def delete_supplier(sid):
    conn = get_conn()
    conn.execute("DELETE FROM suppliers WHERE id=?", (sid,))
    conn.commit()
    conn.close()


# ── CUSTOMER ORDERS ───────────────────────────────────────────────────────────

def get_customer_orders(search="", status_filter="Všetky"):
    conn = get_conn()
    q = "SELECT * FROM customer_orders WHERE 1=1"
    params = []
    if search:
        q += " AND (customer_name LIKE ? OR products LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if status_filter != "Všetky":
        q += " AND status=?"
        params.append(status_filter)
    q += " ORDER BY order_date DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_customer_order(customer_name, products, amount, status, notes, order_date, customer_id=None):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO customer_orders (customer_id, customer_name, products, amount, status, notes, order_date, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (customer_id, customer_name, products, amount, status, notes, order_date, now)
    )
    conn.commit()
    conn.close()


def update_customer_order_status(order_id, status, notes):
    conn = get_conn()
    conn.execute(
        "UPDATE customer_orders SET status=?, notes=? WHERE id=?",
        (status, notes, order_id)
    )
    conn.commit()
    conn.close()


def delete_customer_order(order_id):
    conn = get_conn()
    conn.execute("DELETE FROM customer_orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()


# ── SUPPLIER ORDERS ───────────────────────────────────────────────────────────

def get_supplier_orders(status_filter="Všetky"):
    conn = get_conn()
    q = "SELECT * FROM supplier_orders WHERE 1=1"
    params = []
    if status_filter != "Všetky":
        q += " AND status=?"
        params.append(status_filter)
    q += " ORDER BY order_date DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_supplier_order(supplier_name, products, quantity, amount, status, deadline, notes, order_date, supplier_id=None):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO supplier_orders (supplier_id, supplier_name, products, quantity, amount, status, deadline, notes, order_date, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (supplier_id, supplier_name, products, quantity, amount, status, deadline, notes, order_date, now)
    )
    conn.commit()
    conn.close()


def update_supplier_order_status(order_id, status, notes):
    conn = get_conn()
    conn.execute(
        "UPDATE supplier_orders SET status=?, notes=? WHERE id=?",
        (status, notes, order_id)
    )
    conn.commit()
    conn.close()


def delete_supplier_order(order_id):
    conn = get_conn()
    conn.execute("DELETE FROM supplier_orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()


# ── CALENDAR ──────────────────────────────────────────────────────────────────

def get_events(month=None, year=None):
    conn = get_conn()
    if month and year:
        prefix = f"{year}-{month:02d}"
        rows = conn.execute(
            "SELECT * FROM calendar_events WHERE event_date LIKE ? ORDER BY event_date",
            (f"{prefix}%",)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM calendar_events ORDER BY event_date").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_upcoming_events(days=30):
    conn = get_conn()
    today = datetime.now().date().isoformat()
    rows = conn.execute(
        "SELECT * FROM calendar_events WHERE event_date >= ? ORDER BY event_date LIMIT 20",
        (today,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_event(title, event_type, event_date, description, created_by):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO calendar_events (title, event_type, event_date, description, created_by, created_at) VALUES (?,?,?,?,?,?)",
        (title, event_type, event_date, description, created_by, now)
    )
    conn.commit()
    conn.close()


def delete_event(event_id):
    conn = get_conn()
    conn.execute("DELETE FROM calendar_events WHERE id=?", (event_id,))
    conn.commit()
    conn.close()


# ── FINANCES ──────────────────────────────────────────────────────────────────

def get_finances(year=None, month=None):
    conn = get_conn()
    q = "SELECT * FROM finances WHERE 1=1"
    params = []
    if year:
        q += " AND date LIKE ?"
        params.append(f"{year}%")
    if month:
        q += " AND date LIKE ?"
        params.append(f"%-{month:02d}-%")
    q += " ORDER BY date DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_finance(type_, category, amount, description, date):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO finances (type, category, amount, description, date, created_at) VALUES (?,?,?,?,?,?)",
        (type_, category, amount, description, date, now)
    )
    conn.commit()
    conn.close()


def delete_finance(fid):
    conn = get_conn()
    conn.execute("DELETE FROM finances WHERE id=?", (fid,))
    conn.commit()
    conn.close()


def get_finance_summary():
    conn = get_conn()
    total_in = conn.execute("SELECT COALESCE(SUM(amount),0) FROM finances WHERE type='Príjem'").fetchone()[0]
    total_out = conn.execute("SELECT COALESCE(SUM(amount),0) FROM finances WHERE type='Výdavok'").fetchone()[0]
    conn.close()
    return {"income": total_in, "expenses": total_out, "profit": total_in - total_out}


# ── MARKETING ─────────────────────────────────────────────────────────────────

def get_marketing(status_filter="Všetky"):
    conn = get_conn()
    if status_filter != "Všetky":
        rows = conn.execute(
            "SELECT * FROM marketing WHERE status=? ORDER BY planned_date DESC",
            (status_filter,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM marketing ORDER BY planned_date DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_marketing(title, channel, status, planned_date, notes):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO marketing (title, channel, status, planned_date, notes, created_at) VALUES (?,?,?,?,?,?)",
        (title, channel, status, planned_date, notes, now)
    )
    conn.commit()
    conn.close()


def update_marketing(mid, status, result, published_date):
    conn = get_conn()
    conn.execute(
        "UPDATE marketing SET status=?, result=?, published_date=? WHERE id=?",
        (status, result, published_date, mid)
    )
    conn.commit()
    conn.close()


def delete_marketing(mid):
    conn = get_conn()
    conn.execute("DELETE FROM marketing WHERE id=?", (mid,))
    conn.commit()
    conn.close()


# ── DASHBOARD STATS ───────────────────────────────────────────────────────────

def get_dashboard_stats():
    conn = get_conn()
    stats = {}
    stats["customers"] = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    stats["cust_orders"] = conn.execute("SELECT COUNT(*) FROM customer_orders").fetchone()[0]
    stats["cust_orders_new"] = conn.execute("SELECT COUNT(*) FROM customer_orders WHERE status='Nová'").fetchone()[0]
    stats["supp_orders"] = conn.execute("SELECT COUNT(*) FROM supplier_orders").fetchone()[0]
    stats["supp_orders_pending"] = conn.execute(
        "SELECT COUNT(*) FROM supplier_orders WHERE status NOT IN ('Doručená','Zrušená')"
    ).fetchone()[0]
    fin = get_finance_summary()
    stats["income"] = fin["income"]
    stats["expenses"] = fin["expenses"]
    stats["profit"] = fin["profit"]
    stats["upcoming_events"] = conn.execute(
        "SELECT COUNT(*) FROM calendar_events WHERE event_date >= date('now')"
    ).fetchone()[0]
    conn.close()
    return stats
