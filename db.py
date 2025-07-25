# db.py
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  bio TEXT NOT NULL,
                  price REAL DEFAULT NULL,
                  image_path TEXT NOT NULL,
                  category_id INTEGER NOT NULL,
                  created_at TEXT NOT NULL,
                  discount_percent REAL DEFAULT 0,
                  is_trending INTEGER DEFAULT 0,
                  contact_link TEXT DEFAULT NULL,
                  FOREIGN KEY (category_id) REFERENCES categories (id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  admin_id INTEGER NOT NULL,
                  action TEXT NOT NULL,
                  details TEXT,
                  timestamp TEXT NOT NULL)''')
    c.execute("INSERT OR IGNORE INTO categories (name) VALUES ('Creators')")
    conn.commit()
    conn.close()

def add_category(name, admin_id):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    c.execute("SELECT id FROM categories WHERE name = ?", (name,))
    cat_id = c.fetchone()[0]
    conn.close()
    log_action(admin_id, "Added category", name)
    return cat_id

def get_categories():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM categories")
    cats = c.fetchall()
    conn.close()
    return cats

def add_product(title, bio, price, image_path, category_id, discount_percent, is_trending, admin_id, contact_link=None):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    created_at = datetime.now().isoformat()
    c.execute("""INSERT INTO products (title, bio, price, image_path, category_id, created_at, discount_percent, is_trending, contact_link)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (title, bio, price, image_path, category_id, created_at, discount_percent, is_trending, contact_link))
    conn.commit()
    conn.close()
    log_action(admin_id, "Added product", title)

def get_products():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("""SELECT p.*, c.name as category_name FROM products p
                 JOIN categories c ON p.category_id = c.id
                 ORDER BY c.name, p.id DESC""")
    products = c.fetchall()
    conn.close()
    return products

def get_admins():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM admins")
    admins = [row[0] for row in c.fetchall()]
    conn.close()
    return admins

def add_admin(user_id):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def log_action(admin_id, action, details=None):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO logs (admin_id, action, details, timestamp) VALUES (?, ?, ?, ?)", (admin_id, action, details, timestamp))
    conn.commit()
    conn.close()

def get_user_logs(user_id):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT action, details, timestamp FROM logs WHERE admin_id = ? ORDER BY timestamp DESC", (user_id,))
    logs = c.fetchall()
    conn.close()
    return logs
