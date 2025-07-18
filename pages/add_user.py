import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])   

supabase = init_connection()
st.title("Add User Information")


st.header("Sign Up")

# Create a form
with st.form(key="signup_form"):
    username = st.text_input("Username")
    password = st.text_input("Password")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    role = st.selectbox("Crew Position", ["General Manager", "Assistant General Manager", "Team Lead", "Crew Member", "Other"])
    submit_button = st.form_submit_button(label="Submit")

# Insert data when the form is submitted
if submit_button:
    data = {"username": username, "password": password, "first_name": first_name, "last_name": last_name, "type": role}
    response = supabase.table("login").insert(data).execute()
    
    if response.data:
        st.success("Data added successfully!")
        st.switch_page("landing.py")
    else:
        st.error("Error adding data!")

# Add a "Back" button to return to the main page
if st.button("Back to Home"):
    st.switch_page("landing.py")