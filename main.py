st.write("---")
    st.header("🛒 Secure Checkout & Delivery")
    
    if st.session_state.cart:
        total = sum(details['price'] * details['qty'] for details in st.session_state.cart.values())
        
        # ছবিটার মতো সুন্দর বক্স বা পপআপ স্টাইল কন্টেইনার
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