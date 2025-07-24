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
                  price REAL NOT NULL,
                  image_url TEXT NOT NULL,
                  category_id INTEGER NOT NULL,
                  created_at TEXT NOT NULL,
                  discount_percent REAL DEFAULT 0,
                  is_trending INTEGER DEFAULT 0,
                  FOREIGN KEY (category_id) REFERENCES categories (id))''')
    conn.commit()
    conn.close()

def add_category(name):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    c.execute("SELECT id FROM categories WHERE name = ?", (name,))
    cat_id = c.fetchone()[0]
    conn.close()
    return cat_id

def get_categories():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM categories")
    cats = c.fetchall()
    conn.close()
    return cats

def add_product(title, bio, price, image_url, category_id, discount_percent, is_trending):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    created_at = datetime.now().isoformat()
    c.execute("""INSERT INTO products (title, bio, price, image_url, category_id, created_at, discount_percent, is_trending)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (title, bio, price, image_url, category_id, created_at, discount_percent, is_trending))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("""SELECT p.*, c.name as category_name FROM products p
                 JOIN categories c ON p.category_id = c.id
                 ORDER BY c.name, p.id DESC""")
    products = c.fetchall()
    conn.close()
    return products

# Add more functions if needed for edit/delete
