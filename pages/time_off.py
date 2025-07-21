import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, timedelta

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]) 

supabase = init_connection()

# Navigation Bar
st.sidebar.page_link('pages/home.py', label='Home')
st.sidebar.page_link('pages/message.py', label='Messages')
st.sidebar.page_link('pages/calendar.py', label='Schedule')
st.sidebar.page_link('pages/chart.py', label='Statistics')

st.header("Time-Off Requests")

response_log = supabase.table("login").select("first_name", "last_name").eq("id", st.session_state["id"]).single().execute()
data_log = response_log.data

resposne_off = supabase.table("time_off").select("*").eq("id", st.session_state["id"]).execute()
data_off = resposne_off.data

# Form to send data to supabase
with st.form(key="room_form"):
    date = st.date_input("Enter requested date:", value=None)
    hours = st.text_input("How many hours:")
    
    if st.form_submit_button("Submit"):
        data = {
            "id":st.session_state["id"],
            "date":date.isoformat(),
            "hours":hours,
            "first_name": data_log["first_name"],
            "last_name": data_log["last_name"],
            "resolved": "unread"
        }
        response_ins = supabase.table("time_off").insert(data).execute()
            
        if response_ins.data:
            st.success("Data added successfully!")
        else:
            st.error("Error adding data!")

st.subheader("Requests")
for x in data_off[-5:]:
    with st.container():
        dt = datetime.fromisoformat(x['date'])
        date = dt.date().isoformat()
        st.markdown(f"{x['first_name']} {x['last_name']}")
        st.markdown(f"Date requested: {date}")
        st.markdown(f"Hours requested: {x['hours']}")
        st.markdown(f"{x['resolved'].capitalize()}")

if st.button("Back"):
    st.switch_page('pages/calendar.py')