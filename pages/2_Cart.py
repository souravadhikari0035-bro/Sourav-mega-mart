import streamlit as st
import sqlite3

st.set_page_config(page_title="My Cart", page_icon="🛒")

st.title("🛒 Your Shopping Cart")


if 'cart' not in st.session_state or len(st.session_state.cart) == 0:
    st.warning("Your cart is empty! Go to the Store to add some products.")
else:
    total_amount = 0
    
    st.write("### Review Your Items:")
    st.write("---")
    
    
    for item in st.session_state.cart:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{item['name']}**")
        with col2:
            st.write(f"₹{item['price']} x {item['qty']}")
        with col3:
            item_total = item['price'] * item['qty']
            st.write(f"**₹{item_total}**")
            total_amount += item_total
            
    st.write("---")
    st.subheader(f"Total Bill: ₹{total_amount}")
    
    
    if st.button("Proceed to Checkout", type="primary"):
        conn = sqlite3.connect('shop_inventory.db')
        c = conn.cursor()
        
        
        for item in st.session_state.cart:
            c.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item['qty'], item['id']))
            
        conn.commit()
        conn.close()
        
        
        st.session_state.cart = []
        
        st.success("🎉 Checkout Successful! Thank you for shopping with us.")
        st.balloons()