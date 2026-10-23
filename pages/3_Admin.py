import streamlit as st
import sqlite3

st.set_page_config(page_title="Admin Panel", page_icon="⚙️")

st.title("⚙️ Admin Panel - Inventory Management")

conn = sqlite3.connect('shop_inventory.db')
c = conn.cursor()

st.subheader("📦 Current Inventory")

c.execute("SELECT id, name, category, price, stock FROM products")
products = c.fetchall()

if len(products) > 0:
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
    col1.write("**ID**")
    col2.write("**Name**")
    col3.write("**Category**")
    col4.write("**Price**")
    col5.write("**Stock**")
    
    for p in products:
        c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 2, 1])
        c1.write(p[0])
        c2.write(p[1])
        c3.write(p[2])
        c4.write(f"₹{p[3]}")
        c5.write(p[4])
else:
    st.info("Inventory is empty.")

st.write("---")
st.subheader("➕ Add New Product")

with st.form("add_product_form", clear_on_submit=True):
    p_name = st.text_input("Product Name")
    p_category = st.text_input("Category")
    p_price = st.number_input("Price ₹", min_value=0.0, step=10.0)
    p_stock = st.number_input("Stock Quantity", min_value=0, step=1)
    
    submitted = st.form_submit_button("Add Product")
    
    if submitted:
        if p_name != "" and p_category != "":
            c.execute("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)", 
                      (p_name, p_category, p_price, p_stock))
            conn.commit()
            st.success(f"Successfully added {p_name} to inventory! 🎉")
            st.rerun() 
        else:
            st.error("Please fill in all the details.")

conn.close()