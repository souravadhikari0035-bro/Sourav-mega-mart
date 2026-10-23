import streamlit as st


st.set_page_config(
    page_title="Sourav's Mega Mart",
    page_icon="🛒",
)


if 'cart' not in st.session_state:
    st.session_state.cart = []

st.title("🛒 Welcome to Sourav's Mega Mart!")
st.write("---")
st.write("### Welcome to our Professional shopping portal! 🎉")
st.info("👈 Plese select **Store** from the left menu to start shopping.")
st.success("For inventory management, select **Admin** from the left menu.")