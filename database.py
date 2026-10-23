import sqlite3

def init_db():
    
    conn = sqlite3.connect('shop_inventory.db')
    c = conn.cursor()
    
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        sample_products = [
            ('Smartphone', 'Electronics', 15000.0, 10),
            ('Laptop', 'Electronics', 45000.0, 5),
            ('Headphones', 'Accessories', 1500.0, 20),
            ('T-Shirt', 'Clothing', 500.0, 50)
        ]
        c.executemany('INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)', sample_products)
        
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print("Database setup complete! 'shop_inventory.db' file created.")