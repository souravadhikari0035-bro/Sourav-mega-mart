import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="NexaMart", layout="wide")

# ==========================================
# 1. Database Setup with Flipkart-like Products & Correct Images
# ==========================================
def init_db():
    conn = sqlite3.connect('nexamart.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT UNIQUE, 
                    category TEXT, 
                    price REAL, 
                    original_price REAL,
                    description TEXT,
                    rating REAL,
                    stock INTEGER,
                    image TEXT
                )''')
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, name TEXT, password TEXT)')
    
    defaults = [
        ("Wireless Noise-Cancelling Headphones", "Electronics", 3499.0, 5999.0, "Active Noise Cancellation, 40-hour battery life, crystal-clear hands-free calling.", 4.7, 14, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"),
        ("Smart Fitness Watch with SpO2", "Electronics", 2199.0, 3999.0, "AMOLED Display, 24/7 Heart Rate Monitoring, SpO2 tracker, 7-day battery backup.", 4.5, 20, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"),
        ("USB-C Multiport Hub Adapter", "Electronics", 1499.0, 2499.0, "4K HDMI, 3x USB 3.0 ports, Power Delivery fast charging support.", 4.6, 12, "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500"),
        ("Fresh Organic Apples (1kg)", "Grocery", 200.0, 250.0, "Fresh, crisp, and juicy organic apples directly from the farm. Premium quality pack.", 4.8, 50, "https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?w=500"),
        ("Casual Cotton T-Shirt", "Fashion", 500.0, 999.0, "100% pure cotton, breathable fabric, comfortable regular fit for everyday wear.", 4.3, 30, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500"),
        ("Non-Stick Cookware Set (3 Pcs)", "Home & Kitchen", 1899.0, 3499.0, "PFOA-free non-stick coating, induction compatible, sturdy heat-resistant handles.", 4.6, 15, "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500"),
        ("Kids Remote Control Racing Car", "Toys & Kids", 999.0, 1999.0, "High-speed rechargeable RC car with LED lights and anti-skid rubber tires.", 4.4, 25, "https://images.unsplash.com/photo-1594787318286-3d835c1d207f?w=500")
    ]
    
    for p in defaults:
        try:
            c.execute('INSERT INTO products (name, category, price, original_price, description, rating, stock, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', p)
        except sqlite3.IntegrityError:
            c.execute('UPDATE products SET price=?, original_price=?, description=?, rating=?, stock=?, image=? WHERE name=?', (p[2], p[3], p[4], p[5], p[6], p[7], p[0]))
            
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
        st.write("---")
        
        tab_add, tab_update, tab_db = st.tabs(["➕ Add Product", "✏️ Update Specs", "📦 Inventory & Users"])
        
        with tab_add:
            st.subheader("Add Product with Specifications")
            with st.form("add_form"):
                n = st.text_input("Product Name")
                c = st.selectbox("Category", ["Electronics", "Grocery", "Fashion", "Home & Kitchen", "Toys & Kids", "Books"])
                col_p1, col_p2 = st.columns(2)
                with col_p1: p = st.number_input("Selling Price (₹)", min_value=1.0)
                with col_p2: op = st.number_input("Original Price (₹)", min_value=1.0)
                
                desc = st.text_area("Product Description & Specs")
                col_r1, col_r2 = st.columns(2)
                with col_r1: rat = st.number_input("Rating (1-5)", min_value=1.0, max_value=5.0, value=4.5)
                with col_r2: stk = st.number_input("Available Stock", min_value=1, value=10)
                
                img = st.text_input("Image URL")
                
                if st.form_submit_button("Add Product"):
                    try:
                        conn = sqlite3.connect('nexamart.db')
                        conn.cursor().execute('INSERT INTO products (name, category, price, original_price, description, rating, stock, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (n, c, p, op, desc, rat, stk, img))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ '{n}' Added Successfully!")
                        st.rerun()
                    except:
                        st.error("Error! Product name might already exist.")
                        
        with tab_update:
            st.subheader("Update Product Details")
            conn = sqlite3.connect('nexamart.db')
            all_products_df = pd.read_sql_query("SELECT name FROM products", conn)
            
            if not all_products_df.empty:
                selected_product = st.selectbox("Select Product:", all_products_df['name'].tolist())
                curr_data = conn.cursor().execute("SELECT price, original_price, description, rating, stock, image FROM products WHERE name=?", (selected_product,)).fetchone()
                
                with st.form("update_form"):
                    up_p = st.number_input("Selling Price (₹)", value=float(curr_data[0]))
                    up_op = st.number_input("Original Price (₹)", value=float(curr_data[1]))
                    up_desc = st.text_area("Description & Specs", value=curr_data[2] if curr_data[2] else "")
                    up_rat = st.number_input("Rating", value=float(curr_data[3]))
                    up_stk = st.number_input("Stock", value=int(curr_data[4]))
                    up_img = st.text_input("Image URL", value=curr_data[5] if curr_data[5] else "")
                    
                    if st.form_submit_button("Save Changes"):
                        conn.cursor().execute("UPDATE products SET price=?, original_price=?, description=?, rating=?, stock=?, image=? WHERE name=?", (up_p, up_op, up_desc, up_rat, up_stk, up_img, selected_product))
                        conn.commit()
                        st.success(f"✅ '{selected_product}' Updated!")
                        st.rerun()
            conn.close()
            
        with tab_db:
            conn = sqlite3.connect('nexamart.db')
            st.subheader("📦 Live Inventory")
            df_prods = pd.read_sql_query("SELECT * FROM products", conn)
            st.dataframe(df_prods, hide_index=True, use_container_width=True)
            conn.close()

# ==========================================
# 3. Main Storefront Layout
# ==========================================
else:
    h_col1, h_col2, h_col3 = st.columns([1, 2, 1])
    with h_col1:
        st.title("🛒 NexaMart")
    with h_col2:
        search_kw = st.text_input("Search", placeholder="Search for electronics, fashion, groceries, toys...", label_visibility="collapsed")
    with h_col3:
        st.write("")
        if st.session_state.logged_in_email:
            st.success(f"👤 {st.session_state.logged_in_name}")
        else:
            st.info("👤 Browse Mode (Login in Sidebar)")

    # ক্যাটাগরি পিলস / ট্যাব
    selected_cat = st.radio(
        "Categories",
        ["All Products", "Electronics", "Grocery", "Fashion", "Home & Kitchen", "Toys & Kids"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.write("---")

    with st.container(border=True):
        st.caption("LIMITED TIME OFFERS")
        st.header("Elevate Your Everyday Shopping")
        st.write("Flat 10% off on your first order with coupon **WELCOME10**. Use **SAVE50** for ₹50 off on orders over ₹499.")
        st.markdown("🏷️ `WELCOME10` (10% Off) &nbsp;&nbsp;|&nbsp;&nbsp; 🏷️ `SAVE50` (₹50 Off) &nbsp;&nbsp;|&nbsp;&nbsp; 🚚 `FREESHIP` (Free Delivery)")

    st.write("---")

    with st.sidebar:
        st.header("Customer Profile")
        if st.session_state.logged_in_email is None:
            st.info("💡 You can browse products freely without login! Login is only required to add items to cart & checkout.")
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
                        if user_data and user_data[1] == clean_pass:
                            st.session_state.logged_in_email = clean_email
                            st.session_state.logged_in_name = user_data[0]
                            st.rerun()
                        else:
                            st.error("❌ Invalid Credentials!")
            with tab2:
                s_n = st.text_input("Full Name")
                s_e = st.text_input("New Email")
                s_p = st.text_input("New Password", type="password")
                if st.button("Create Profile", use_container_width=True):
                    if s_n and s_e and s_p:
                        try:
                            conn = sqlite3.connect('nexamart.db')
                            conn.cursor().execute('INSERT INTO users VALUES (?, ?, ?)', (s_e.strip().lower(), s_n, s_p.strip()))
                            conn.commit()
                            conn.close()
                            st.success("✅ Profile Created! Please Login.")
                        except:
                            st.error("⚠️ Email already exists!")
        else:
            st.write(f"**Email:** {st.session_state.logged_in_email}")
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in_email = None
                st.session_state.logged_in_name = None
                st.session_state.cart = {}
                st.rerun()

        st.divider()
        cart_total_items = sum(item['qty'] for item in st.session_state.cart.values())
        cart_total_price = sum(details['price'] * details['qty'] for details in st.session_state.cart.values())
        st.header(f"🛒 Cart ({cart_total_items}) - ₹{cart_total_price:,.2f}")
        
        if not st.session_state.cart:
            st.write("Your Cart is Empty")
        else:
            for item, details in list(st.session_state.cart.items()):
                sub = details['price'] * details['qty']
                st.write(f"**{item}** (x{details['qty']}) - ₹{sub}")
                if st.button(f"Remove {item}", key=f"del_{item}"):
                    del st.session_state.cart[item]
                    st.rerun()

    conn = sqlite3.connect('nexamart.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    if selected_cat != "All Products":
        df = df[df['category'] == selected_cat]

    if search_kw:
        df = df[df['name'].str.contains(search_kw, case=False) | df['description'].str.contains(search_kw, case=False)]

    st.subheader(f"Showing Products: {selected_cat}")

    if df.empty:
        st.warning("No products found in this category.")
    else:
        for idx, row in df.iterrows():
            with st.container(border=True):
                col_img, col_info, col_buy = st.columns([1, 2, 1])
                
                with col_img:
                    if row["image"]:
                        st.image(row["image"], use_container_width=True)
                        
                with col_info:
                    st.subheader(row['name'])
                    st.caption(f"Category: {row['category']}")
                    
                    st.markdown(f"⭐ **{row['rating']}** | <span style='color:green;'>✓ In Stock ({row['stock']} available units)</span>", unsafe_allow_html=True)
                    
                    if row['original_price'] and row['original_price'] > row['price']:
                        discount = int(((row['original_price'] - row['price']) / row['original_price']) * 100)
                        st.markdown(f"### ₹{row['price']:,.2f} &nbsp; <del style='color:gray;font-size:16px;'>₹{row['original_price']:,.2f}</del> &nbsp; <span style='background-color:#d4edda;color:#155724;padding:2px 6px;font-size:12px;border-radius:4px;'>Save {discount}%</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"### ₹{row['price']:,.2f}")
                        
                    if row['description']:
                        st.write(f"📝 {row['description']}")
                        
                with col_buy:
                    st.write("")
                    st.write("")
                    # লগইন চেক: লগইন না থাকলে কার Noi যোগ করতে দেবে না, লগইন করতে বলবে
                    if st.button("Add to Cart 🛒", key=f"add_{row['id']}", use_container_width=True):
                        if st.session_state.logged_in_email is None:
                            st.warning("⚠️ কার্টে প্রোডাক্ট যোগ করতে হলে আগে সাইডবার থেকে লগইন বা সাইন আপ করুন!")
                        else:
                            if row['name'] in st.session_state.cart:
                                st.session_state.cart[row['name']]['qty'] += 1
                            else:
                                st.session_state.cart[row['name']] = {'price': row['price'], 'qty': 1}
                            st.toast(f"Added {row['name']} to cart!")

    st.write("---")
    st.header("🛒 Secure Checkout & Delivery")
    
    if st.session_state.cart:
        if st.session_state.logged_in_email is None:
            st.warning("⚠️ চেকআউট ও পেমেন্ট করতে হলে অনুগ্রহ করে আগে সাইডবার থেকে লগইন করুন!")
        else:
            total = sum(details['price'] * details['qty'] for details in st.session_state.cart.values())
            with st.container(border=True):
                col_form, col_summary = st.columns([2, 1])
                with col_form:
                    st.subheader("1. Delivery Address")
                    with st.form("checkout_form"):
                        f_name = st.text_input("Full Name *", value=st.session_state.get('logged_in_name', ''))
                        f_phone = st.text_input("Contact Phone *", placeholder="+91 98765 43210")
                        f_email = st.text_input("Email Address *", value=st.session_state.get('logged_in_email', ''))
                        f_address = st.text_input("Street Address / House No. *", placeholder="e.g. 124 Park Avenue")
                        
                        c_city, c_state, c_pin = st.columns(3)
                        with c_city: f_city = st.text_input("City *", placeholder="Kolkata")
                        with c_state: f_state = st.text_input("State *", placeholder="West Bengal")
                        with c_pin: f_pin = st.text_input("PIN Code *", placeholder="700001")
                            
                        st.write("---")
                        st.subheader("2. Select Payment Method")
                        pay_method = st.radio("Choose option:", ["Cash on Delivery (COD)", "Instant UPI / QR", "Debit / Credit Card"], label_visibility="collapsed")
                        
                        if st.form_submit_button("Place Secure Order", use_container_width=True, type="primary"):
                            if f_name and f_phone and f_email and f_address and f_city and f_pin:
                                st.success(f"🎉 Order Confirmed for {f_name}! We will ship to {f_city}.")
                                st.balloons()
                                st.session_state.cart = {}
                            else:
                                st.warning("⚠️ Please fill in all mandatory fields marked with *")
                with col_summary:
                    st.subheader("Order Summary")
                    st.write("---")
                    for item, details in st.session_state.cart.values() if isinstance(st.session_state.cart.values(), list) else st.session_state.cart.items():
                        # handle dict loop safely
                        pass
                    for item, details in st.session_state.cart.items():
                        st.write(f"**{item}** x {details['qty']}")
                        st.caption(f"₹{details['price'] * details['qty']:,.2f}")
                    st.write("---")
                    st.markdown(f"### Payable: ₹{total:,.2f}")
    else:
        st.info("Your shopping cart is empty.")