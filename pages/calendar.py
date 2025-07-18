import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, timedelta

# Navigation Bar
st.sidebar.page_link('pages/home.py', label='Home')
st.sidebar.page_link('pages/message.py', label='Messages')
st.sidebar.page_link('pages/calendar.py', label='Schedule')
st.sidebar.page_link('pages/chart.py', label='Statistics')

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]) 

supabase = init_connection()
    
try:
    response = supabase.table("schedule").select("first_name, last_name, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday").execute()
    data = response.data

    response_off = supabase.table("time_off").select("*").eq("resolved", "unread").execute()
    data_off = response_off.data

except Exception:
    data = None


def get_week():
    today = datetime.today().date()
    weekday = today.weekday()

    days_to_sunday = 0 if weekday == 6 else weekday + 1
    start_date = today - timedelta(days = days_to_sunday)
    end_date = start_date + timedelta(days=6)
    return f"{start_date.strftime('%B %d')} - {end_date.strftime('%d, %Y')}".replace(' 0', ' ')

st.subheader('Schedule')

st.write(f"For {get_week()}")

df = pd.DataFrame(data)
df['Name'] = df['last_name'] + ', ' + df['first_name']
df = df.drop(columns=['first_name', 'last_name'])
cols = ['Name'] + [col for col in df.columns if col != 'Name']
df = df[cols]

st.dataframe(df)

if st.button("Edit Availability"):
    st.switch_page('pages/availability.py')

if st.button("Request Time Off"):
    st.switch_page('pages/time_off.py')

if st.session_state.get('type') in ["General Manager", "Assistant General Manager"]:
    if st.button("Set Schedule"):
        st.switch_page("pages/schedule.py")

st.write("Time Off Requests")
for x in data_off:
    with st.container():
        dt = datetime.fromisoformat(x['date'])
        date = dt.date().isoformat()
        st.markdown(f"{x['first_name']} {x['last_name']}")
        st.markdown(f"Date requested: {date}")
        st.markdown(f"Hours requested: {x["hours"]}")
        if st.button("Accept", key=f"accept_{x['request_id']}"):
            supabase.table("time_off").update({"resolved":"approved"}).eq("request_id", x["request_id"]).execute()
            st.rerun()
        if st.button("Deny", key=f"deny_{x['request_id']}"):
            supabase.table("time_off").update({"resolved":"denied"}).eq("request_id", x["request_id"]).execute()
            st.rerun()

    
