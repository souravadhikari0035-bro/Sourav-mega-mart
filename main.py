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
# 2. Secret Admin Panel
# ==========================================
if st.query_params.get("admin") == "true":
    st.title("⚙️ NexaMart Admin Panel")
    admin_pass = st.text_input("Enter Password:", type="password")
    if admin_pass == "sourav123":
        st.success("Admin Logged In")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Add Product")
            with st.form("add"):
                n = st.text_input("Name")
                c = st.selectbox("Category", ["Electronics", "Grocery", "Fashion", "Home & Kitchen", "Beauty", "Books"])
                p = st.number_input("Price", min_value=1)
                img = st.text_input("Image URL")
                if st.form_submit_button("Add to Store"):
                    conn = sqlite3.connect('nexamart.db')
                    conn.cursor().execute('INSERT INTO products (name, category, price, image) VALUES (?, ?, ?, ?)', (n, c, p, img))
                    conn.commit()
                    conn.close()
                    st.rerun()
        with col2:
            conn = sqlite3.connect('nexamart.db')
            st.subheader("📦 Inventory")
            df_prods = pd.read_sql_query("SELECT * FROM products", conn)
            st.dataframe(df_prods, hide_index=True)
            
            st.subheader("👥 Registered Users")
            df_users = pd.read_sql_query("SELECT email, name, password FROM users", conn)
            st.dataframe(df_users, hide_index=True)
            conn.close()

# ==========================================
# 3. NexaMart Original Layout
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
            
            # --- SMART LOGIN SYSTEM ---
            with tab1:
                l_e = st.text_input("Email")
                l_p = st.text_input("Password", type="password")
                if st.button("Login", use_container_width=True):
                    if l_e and l_p:
                        # ডাটা ক্লিনিং (অদৃশ্য স্পেস ও ক্যাপিটাল লেটার দূর করা)
                        clean_email = l_e.strip().lower()
                        clean_pass = l_p.strip()
                        
                        conn = sqlite3.connect('nexamart.db')
                        user_data = conn.cursor().execute("SELECT name, password FROM users WHERE email=?", (clean_email,)).fetchone()
                        conn.close()
                        
                        if user_data:
                            db_name, db_pass = user_data
                            if db_pass == clean_pass:
                                st.session_state.logged_in_email = clean_email
                                st.session_state.logged_in_name = db_name
                                st.rerun()
                            else:
                                st.error("❌ Incorrect Password! (পাসওয়ার্ড ভুল হচ্ছে)")
                        else:
                            st.error("❌ Email not registered! (এই ইমেইলটি ডাটাবেসে নেই)")
                    else:
                        st.warning("Please enter both email and password.")
            
            # --- SMART SIGN UP SYSTEM ---
            with tab2:
                s_n = st.text_input("Full Name")
                s_e = st.text_input("New Email")
                s_p = st.text_input("New Password", type="password")
                if st.button("Create Profile", use_container_width=True):
                    if s_n and s_e and s_p:
                        # ডাটা ক্লিনিং 
                        clean_email = s_e.strip().lower()
                        clean_pass = s_p.strip()
                        try:
                            conn = sqlite3.connect('nexamart.db')
                            conn.cursor().execute('INSERT INTO users VALUES (?, ?, ?)', (clean_email, s_n, clean_pass))
                            conn.commit()
                            conn.close()
                            st.success("✅ Profile Created! Please go to the Login tab.")
                        except sqlite3.IntegrityError:
                            st.error("⚠️ This Email is already registered!")
                    else:
                        st.warning("Please fill all the details.")
        else:
            st.write(f"**Email:** {st.session_state.logged_in_email}")
            st.success("Verified NexaMart Customer")
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in_email, st.session_state.logged_in_name, st.session_state.cart = None, None, {}
                st.rerun()

        st.divider()
        st.header(f"Shopping Cart ({sum(item['qty'] for item in st.session_state.cart.values())})")
        if not st.session_state.cart:
            st.write("Your Cart is Empty")
        else:
            total = 0
            for item, details in list(st.session_state.cart.items()):
                sub = details['price'] * details['qty']
                total += sub
                st.write(f"**{item}** (x{details['qty']}) - ₹{sub}")
                if st.button(f"Remove {item}", key=f"del_{item}"):
                    del st.session_state.cart[item]
                    st.rerun()
            st.write(f"**Subtotal: ₹{total}**")

    conn = sqlite3.connect('nexamart.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    st.subheader("All Products")
    c1, c2 = st.columns([2, 1])
    with c1:
        cats = ["All"] + list(df['category'].unique())
        selected_cat = st.selectbox("Filter by Category", cats, label_visibility="collapsed")
    with c2:
        sort_by = st.selectbox("Sort By", ["Default", "Price: Low to High", "Price: High to Low"], label_visibility="collapsed")

    if search_kw:
        df = df[df['name'].str.contains(search_kw, case=False)]
    if selected_cat != "All":
        df = df[df['category'] == selected_cat]
        
    if sort_by == "Price: Low to High":
        df = df.sort_values(by="price", ascending=True)
    elif sort_by == "Price: High to Low":
        df = df.sort_values(by="price", ascending=False)

    st.write(f"Showing {len(df)} products")
    
    if df.empty:
        st.warning("No products found.")
    else:
        cols = st.columns(4)
        for idx, row in df.iterrows():
            with cols[idx % 4]:
                with st.container(border=True):
                    st.image(row["image"], use_container_width=True)
                    st.write(f"**{row['name']}**")
                    st.caption(row['category'])
                    st.write(f"**₹{row['price']}**")
                    if st.button("Add to Cart", key=f"add_{row['id']}", use_container_width=True):
                        if row['name'] in st.session_state.cart:
                            st.session_state.cart[row['name']]['qty'] += 1
                        else:
                            st.session_state.cart[row['name']] = {'price': row['price'], 'qty': 1}
                        st.toast(f"Added {row['name']} to cart!")

    st.write("---")
    st.header("Secure Checkout")
    if st.session_state.cart:
        total = sum(details['price'] * details['qty'] for details in st.session_state.cart.values())
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("Order Summary")
            st.write(f"Items Subtotal: ₹{total}")
            cpn = st.text_input("Have a coupon?")
            discount = total * 0.10 if cpn == "WELCOME10" else (50 if cpn == "SAVE50" and total > 499 else 0)
            if discount: st.success(f"Discount: -₹{discount}")
            elif cpn: st.error("Invalid code")
            final = total - discount
            st.write(f"**Payable Amount: ₹{final}**")
        with col_c2:
            st.write("")
            st.write("")
            if st.session_state.logged_in_email is None:
                st.warning("Please sign in from the sidebar to proceed.")
            else:
                if st.button("Confirm Order", type="primary", use_container_width=True):
                    st.success(f"Order Confirmed for {st.session_state.logged_in_name}! ID: NM-00123")
                    st.balloons()
                    st.session_state.cart = {}
    else:
        st.info("Your cart is empty.")
        
    st.write("---")
    st.caption("© 2026 NexaMart Inc. Built with Python and Streamlit. Educational Demonstration Platform.")