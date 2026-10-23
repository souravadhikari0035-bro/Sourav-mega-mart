import streamlit as st
import sqlite3

st.set_page_config(page_title="Sourav's Mega Mart", layout="wide")

# ==========================================
# Database Setup (Permanent Storage)
# ==========================================
def init_db():
    conn = sqlite3.connect('mega_mart.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            name TEXT UNIQUE,
            price REAL,
            image TEXT
        )
    ''')
    
    # Add 4 default products if the database is empty
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        defaults = [
            ("Laptop", 50000, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500"),
            ("Smartphone", 15000, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500"),
            ("Headphones", 2000, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"),
            ("Smartwatch", 3500, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500")
        ]
        c.executemany('INSERT INTO products (name, price, image) VALUES (?, ?, ?)', defaults)
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect('mega_mart.db')
    c = conn.cursor()
    c.execute('SELECT name, price, image FROM products')
    data = c.fetchall()
    conn.close()
    return {row[0]: {"price": row[1], "image": row[2]} for row in data}

def add_new_product(name, price, image):
    conn = sqlite3.connect('mega_mart.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO products (name, price, image) VALUES (?, ?, ?)', (name, price, image))
        conn.commit()
        success = True
    except:
        success = False 
    conn.close()
    return success

# Initialize database and load products
init_db()
db_products = get_all_products()

# Initialize session state for cart (Temporary memory)
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# ==========================================
# Main Website UI
# ==========================================
st.title("🛍️ Sourav's Mega Mart")
st.write("Welcome to our professional shopping portal!")
st.divider()

# 1. Product Section
st.header("📦 Our Products")

cols = st.columns(4)
for i, (name, details) in enumerate(db_products.items()):
    with cols[i % 4]:
        st.image(details["image"], use_container_width=True)
        st.subheader(name)
        st.write(f"**Price: ₹{details['price']}**")
        
        if st.button(f"Add to Cart", key=f"add_{name}"):
            if name in st.session_state.cart:
                st.session_state.cart[name] += 1
            else:
                st.session_state.cart[name] = 1
            st.success(f"{name} added!")
            st.rerun()

st.divider()

# 2. Cart Section
st.header("🛒 Your Cart")

if not st.session_state.cart:
    st.info("Your cart is empty. Add some products!")
else:
    total_price = 0
    for name, qty in list(st.session_state.cart.items()):
        if name in db_products:
            price = db_products[name]["price"]
            item_total = price * qty
            total_price += item_total
            
            col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 2])
            col1.write(f"**{name}**")
            col2.write(f"₹{price} x {qty}")
            
            if col3.button("➕", key=f"plus_{name}"):
                st.session_state.cart[name] += 1
                st.rerun()
                
            if col4.button("➖", key=f"minus_{name}"):
                if st.session_state.cart[name] > 1:
                    st.session_state.cart[name] -= 1
                else:
                    del st.session_state.cart[name]
                st.rerun()
                
            col5.write(f"**₹{item_total}**")
        
    st.subheader(f"Total Amount: ₹{total_price}")
    
    # Checkout button with animation
    if st.button("Proceed to Checkout", type="primary"):
        st.success("🎉 Order Confirmed! 👍 Thank you for shopping at Sourav's Mega Mart.")
        st.balloons()
        st.session_state.cart = {}

st.divider()

# 3. Admin Panel
st.header("🔒 Admin Panel")
st.write("Only authorized admins can add new products.")

admin_pass = st.text_input("Enter Admin Password:", type="password")

if admin_pass == "sourav123": 
    st.success("Login Successful! Welcome Admin Sourav.")
    
    st.write("### Add a New Product")
    new_name = st.text_input("Product Name (e.g., DSLR Camera)")
    new_price = st.number_input("Product Price (₹)", min_value=1.0)
    new_image = st.text_input("Product Image URL (Paste link here)")
    
    if st.button("Add Product to Store"):
        if new_name and new_price and new_image:
            if add_new_product(new_name, new_price, new_image):
                st.success(f"'{new_name}' added successfully to the store permanently!")
                st.rerun()
            else:
                st.error("This product name already exists!")
        else:
            st.error("Please fill in all details (Name, Price, and Image URL).")
            
elif admin_pass != "":
    st.error("Incorrect Password! Access Denied.")