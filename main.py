import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="NexaMart", layout="wide")

# ==========================================
# 1. Database Setup
# ==========================================
def init_db():
    conn = sqlite3.connect('nexamart.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, category TEXT, price REAL, image TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, name TEXT, password TEXT)')
    
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        defaults = [
            ("Smart TV 4K", "Electronics", 35000, "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500"),
            ("Smartphone Pro", "Electronics", 45000, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500"),
            ("Fresh Apples", "Grocery", 200, "https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?w=500"),
            ("Casual T-Shirt", "Fashion", 500, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500"),
            ("Coffee Mug Set", "Home & Kitchen", 350, "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=500")
        ]
        c.executemany('INSERT INTO products (name, category, price, image) VALUES (?, ?, ?, ?)', defaults)
    conn.commit()
    conn.close()

init_db()

if 'logged_in_email' not in st.session_state:
    st.session_state.logged_in_email = None
if 'logged_in_name' not in st.session_state:
    st.session_state.logged_in_name = None
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# ==========================================
# 2. Advanced Admin Panel
# ==========================================
if st.query_params.get("admin") == "true":
    st.title("⚙️ NexaMart Admin Panel")
    admin_pass = st.text_input("Enter Password:", type="password")
    
    if admin_pass == "sourav123":
        st.success("Admin Logged In")
        st.write("---")
        
        tab_add, tab_update, tab_db = st.tabs(["➕ Add New Product", "✏️ Update Product", "📦 Inventory & Users"])
        
        with tab_add:
            st.subheader("Add Product to Store")
            with st.form("add_form"):
                n = st.text_input("Name")
                c = st.selectbox("Category", ["Electronics", "Grocery", "Fashion", "Home & Kitchen", "Beauty", "Books"])
                p = st.number_input("Price (₹)", min_value=1)
                img = st.text_input("Image URL (Paste Link)")
                if st.form_submit_button("Add Product"):
                    try:
                        conn = sqlite3.connect('nexamart.db')
                        conn.cursor().execute('INSERT INTO products (name, category, price, image) VALUES (?, ?, ?, ?)', (n, c, p, img))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ '{n}' Added Successfully!")
                        st.rerun()
                    except:
                        st.error("Error! Product name might already exist.")
                        
        with tab_update:
            st.subheader("Update Existing Product Image or Price")
            conn = sqlite3.connect('nexamart.db')
            all_products_df = pd.read_sql_query("SELECT name FROM products", conn)
            
            if not all_products_df.empty:
                selected_product = st.selectbox("Select a Product to Update:", all_products_df['name'].tolist())
                curr_data = conn.cursor().execute("SELECT price, image FROM products WHERE name=?", (selected_product,)).fetchone()
                
                with st.form("update_form"):
                    new_price = st.number_input("Update Price (₹)", value=float(curr_data[0]), min_value=1.0)
                    new_image = st.text_input("New Image URL", value=curr_data[1] if curr_data[1] else "")
                    
                    if st.form_submit_button("Save Changes"):
                        conn.cursor().execute("UPDATE products SET price=?, image=? WHERE name=?", (new_price, new_image, selected_product))
                        conn.commit()
                        st.success(f"✅ '{selected_product}' Updated Successfully!")
                        st.rerun()
            conn.close()
            
        with tab_db:
            conn = sqlite3.connect('nexamart.db')
            st.subheader("📦 Live Inventory")
            df_prods = pd.read_sql_query("SELECT * FROM products", conn)
            st.dataframe(df_prods, hide_index=True, use_container_width=True)
            
            st.subheader("👥 Registered Users")
            df_users = pd.read_sql_query("SELECT email, name, password FROM users", conn)
            st.dataframe(df_users, hide_index=True, use_container_width=True)
            conn.close()

# ==========================================
# 3. NexaMart Original Layout (Store & Checkout)
# ==========================================
else:
    st.markdown("<div style='background-color:#ffe6e6; padding:8px; text-align:center; color:#cc0000;'><b>Festive Sale:</b> Use coupon <b>WELCOME10</b> for 10% off | Free Delivery on orders over ₹999</div>", unsafe_allow_html=True)
    
    st.write("")
    h_col1, h_col2, h_col3 = st.columns([1, 2, 1])
    with h_col1:
        st.title("🛒 NexaMart")
    with h_col2:
        search_kw = st.text_input("Search", placeholder="Search for products, brands and more...", label_visibility="collapsed")
    with h_col3:
        st.write("")
        if st.session_state.logged_in_email:
            st.success(f"👤 {st.session_state.logged_in_name}")
        else:
            st.info("👤 Guest User (Login from Sidebar)")

    st.write("---")
    st.caption("Limited Time Offers")
    st.header("Elevate Your Everyday Shopping")
    st.write("Flat 10% off on your first order with coupon `WELCOME10`. Use `SAVE50` for ₹50 off on orders over ₹499.")
    st.write("🏷️ **WELCOME10** (10% Off) | 🏷️ **SAVE50** (₹50 Off) | 🏷️ **FREESHIP** (Free Delivery)")
    st.write("---")

    with st.sidebar:
        st.header("Customer Profile")
        if st.session_state.logged_in_email is None:
            st.write("Sign in with any email to proceed with your NexaMart order.")
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                l_e = st.text_input("Email")
                l_p = st.text_input("Password", type="password")
                if st.button("Login", use_container_width=True):
                    if l_e and l_p:
                        clean_email = l_e.strip().lower()
                        clean_pass = l_p.strip()
                        conn = sqlite3.connect('nexamart.db')
                        user_data = conn.cursor().execute("SELECT name, password FROM users WHERE email=?", (clean_email,)).fetchone()
                        conn.close()
                        if user_data:
                            db_name, db_pass = user_data
                            if db_pass == clean_pass:
                                st.session_state.logged_in_