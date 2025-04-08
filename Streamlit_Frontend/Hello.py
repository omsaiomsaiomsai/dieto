import streamlit as st
from streamlit_navigation_bar import st_navbar
from streamlit import session_state as ss
import pages as pg

st.set_page_config(
    page_title="Hello Everyone",
    page_icon="👋",
)

st.write("# Welcome to Dieto! 👋")
st.header(":red[Fuel Your Body, Nourish Your Soul.]")
st.sidebar.page_link('Hello.py', label='Home')
st.sidebar.page_link('pages/Login.py', label='Login')