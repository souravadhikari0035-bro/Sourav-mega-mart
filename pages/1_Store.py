import streamlit as st
import sqlite3

st.set_page_config(page_title="Store", page_icon="🛍️")

st.title("🛍️ Explore Our Products")


if 'cart' not in st.session_state:
    st.session_state.cart = []


conn = sqlite3.connect('shop_inventory.db')
c = conn.cursor()


c.execute("SELECT * FROM products")
products = c.fetchall()

if len(products) == 0:
    st.warning("No products available right now!")
else:
    for product in products:
        
        p_id, p_name, p_category, p_price, p_stock = product
        
        with st.container():
            col1, col2 = st.columns([3, 1]) 
            
            with col1:
                st.subheader(p_name)
                st.write(f"**Category:** {p_category} | **Price:** ₹{p_price} | **Stock:** {p_stock}")
            
            with col2:
                
                if p_stock > 0:
                    if st.button("Add to Cart", key=f"btn_{p_id}"):
                        
                        found = False
                        for item in st.session_state.cart:
                            if item['id'] == p_id:
                                item['qty'] += 1
                                found = True
                                break
                        
                        
                        if not found:
                            st.session_state.cart.append({'id': p_id, 'name': p_name, 'price': p_price, 'qty': 1})
                            
                        st.success(f"{p_name} added to cart! 🛒")
                else:
                    st.error("Out of Stock")
        
        st.divider() 

conn.close()