import streamlit as st

st.set_page_config(page_title="Sourav's Mega Mart", layout="wide")

if 'cart' not in st.session_state:
    st.session_state.cart = {}

if 'products' not in st.session_state:
    st.session_state.products = {
        "Laptop": 50000,
        "Smartphone": 15000,
        "Headphones": 2000,
        "Smartwatch": 3500
    }

st.title("🛍️ Sourav's Mega Mart")
st.write("Welcome to our professional shopping portal!")

st.divider()

# Store Section
st.header("📦 Our Products")

cols = st.columns(4)
for i, (name, price) in enumerate(st.session_state.products.items()):
    with cols[i % 4]:
        # Automatic image generation based on product name
        image_keyword = name.lower().replace(" ", ",")
        auto_image_url = f"https://loremflickr.com/320/240/{image_keyword}"
        
        st.image(auto_image_url, use_container_width=True)
        st.subheader(name)
        st.write(f"**Price: ₹{price}**")
        
        if st.button(f"Add to Cart", key=f"add_{name}"):
            if name in st.session_state.cart:
                st.session_state.cart[name] += 1
            else:
                st.session_state.cart[name] = 1
            st.success(f"{name} added!")
            st.rerun()

st.divider()

# Cart Section
st.header("🛒 Your Cart")

if not st.session_state.cart:
    st.info("Your cart is empty. Add some products!")
else:
    total_price = 0
    for name, qty in list(st.session_state.cart.items()):
        price = st.session_state.products[name]
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
    st.button("Proceed to Checkout", type="primary")

st.divider()

# Admin Panel
st.header("🔒 Admin Panel")
st.write("Only authorized admins can add new products.")

admin_pass = st.text_input("Enter Admin Password:", type="password")

if admin_pass == "sourav123": 
    st.success("Login Successful! Welcome Admin Sourav.")
    
    st.write("### Add a New Product")
    new_name = st.text_input("Product Name (e.g., Shoes, Camera)")
    new_price = st.number_input("Product Price (₹)", min_value=1)
    
    if st.button("Add Product to Store"):
        if new_name and new_price:
            st.session_state.products[new_name] = new_price
            st.success(f"'{new_name}' added successfully! Image will be fetched automatically.")
            st.rerun()
        else:
            st.error("Please enter both Product Name and Price.")
            
elif admin_pass != "":
    st.error("Incorrect Password! Access Denied.")