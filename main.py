import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="NexaMart", layout="wide")

# ==========================================
# 1. Database Setup (Foolproof & Auto-Load)
# ==========================================
def init_db():
    conn = sqlite3.connect('nexamart.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, category TEXT, price REAL, image TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, name TEXT, password TEXT)')
    
    defaults = [
        ("Smart TV 4K", "Electronics", 35000, "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500"),
        ("Smartphone Pro", "Electronics", 45000, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500"),
        ("Fresh Apples", "Grocery", 200, "https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?w=500"),
        ("Casual T-Shirt", "Fashion", 500, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500"),
        ("Coffee Mug Set", "Home & Kitchen", 350, "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=500")
    ]
    # INSERT OR IGNORE ব্যবহার করায় প্রোডাক্টগুলো মিস হওয়ার কোনো সুযোগ নেই
    c.executemany('INSERT OR IGNORE INTO products (name, category, price, image) VALUES (?, ?, ?, ?)', defaults)
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
                                st.session_state.logged_in_email = clean_email
                                st.session_state.logged_in_name = db_name
                                st.rerun()
                            else:
                                st.error("❌ Incorrect Password!")
                        else:
                            st.error("❌ Email not registered!")
                    else:
                        st.warning("Please enter both email and password.")
            
            with tab2:
                s_n = st.text_input("Full Name")
                s_e = st.text_input("New Email")
                s_p = st.text_input("New Password", type="password")
                if st.button("Create Profile", use_container_width=True):
                    if s_n and s_e and s_p:
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
                    if row["image"]:
                        st.image(row["image"], use_container_width=True)
                    else:
                        st.info("Image not available")
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
    st.header("🛒 Secure Checkout & Delivery")
    
    if st.session_state.cart:
        total = sum(details['price'] * details['qty'] for details in st.session_state.cart.values())
        
        with st.container(border=True):
            col_form, col_summary = st.columns([2, 1])
            
            with col_form:
                st.subheader("1. Delivery Address")
                with st.form("checkout_form"):
                    f_name = st.text_input("Full Name *", value=st.session_state.get('logged_in_name', ''))
                    f_phone = st.text_input("Contact Phone *", placeholder="+91 98765 43210")
                    f_email = st.text_input("Email Address *", value=st.session_state.get('logged_in_email', ''))
                    f_address = st.text_input("Street Address / House No. *", placeholder="e.g. 124 Park Avenue, Suite 4B")
                    
                    c_city, c_state, c_pin = st.columns(3)
                    with c_city:
                        f_city = st.text_input("City *", placeholder="Kolkata")
                    with c_state:
                        f_state = st.text_input("State *", placeholder="West Bengal")
                    with c_pin:
                        f_pin = st.text_input("PIN Code *", placeholder="700001")
                        
                    st.write("---")
                    st.subheader("2. Select Payment Method")
                    pay_method = st.radio(
                        "Choose payment option:",
                        [
                            "Cash on Delivery (COD) - Pay upon physical package arrival",
                            "Instant UPI / QR (Educational Demo) - Fast simulated approval",
                            "Debit / Credit Card (Test Gateway) - Safe test order verification"
                        ],
                        label_visibility="collapsed"
                    )
                    
                    st.write("")
                    submitted = st.form_submit_button("Place Secure Order", use_container_width=True, type="primary")
                    
                    if submitted:
                        if f_name and f_phone and f_email and f_address and f_city and f_pin:
                            st.success(f"🎉 Order Confirmed successfully for {f_name}! We will ship to {f_city}, {f_pin}.")
                            st.balloons()
                            st.session_state.cart = {}
                        else:
                            st.warning("⚠️ Please fill in all mandatory fields marked with *")
                            
            with col_summary:
                st.subheader("Order Summary")
                st.write("---")
                for item, details in st.session_state.cart.items():
                    st.write(f"**{item}** x {details['qty']}")
                    st.caption(f"₹{details['price'] * details['qty']:,.2f}")
                
                st.write("---")
                st.write(f"**Subtotal:** ₹{total:,.2f}")
                
                cpn = st.text_input("Have a coupon?")
                discount = total * 0.10 if cpn == "WELCOME10" else (50 if cpn == "SAVE50" and total > 499 else 0)
                if discount: 
                    st.success(f"Discount: -₹{discount:,.2f}")
                elif cpn: 
                    st.error("Invalid code")
                    
                final_payable = total - discount
                st.markdown(f"### Payable: ₹{final_payable:,.2f}")
    else:
        st.info("Your shopping cart is empty. Add products to proceed to checkout.")