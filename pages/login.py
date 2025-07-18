import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])   

supabase = init_connection()

st.header("Log In")

with st.form(key="signup_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    submit_button = st.form_submit_button(label="Submit")

# Insert data when the form is submitted
if submit_button:
    response = supabase.table("login").select("*").eq("username", username).eq("password", password).execute()
    
    if response.data:
        st.success("Log In Successful!")
        st.session_state['id'] = response.data[0]["id"]
        st.session_state['user'] = response.data[0]["first_name"]
        st.session_state['type'] = response.data[0]["type"]
        st.switch_page("pages/home.py")
    else:
        st.error("Incorrect Username/Password")

if st.button("Back"):
    st.switch_page("landing.py")

