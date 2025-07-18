import streamlit as st
import plotly.figure_factory as ff
from supabase import create_client
from streamlit_calendar import calendar
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

st.header("Availability")

try:
    response = supabase.table("availability").select("*").eq("id", st.session_state["id"]).single().execute()
    data = response.data
except Exception:
    data = None
    

def value_set(day):
    # day variable would be the columns in the availability table in supabase
    # ex: mon_start
    if data and data[day] != None:
        return data[day]
    else:
        return None

base_date = "2025-05-04"
days = [
    ("sun_start", "sun_end", "Sunday", "2025-05-04"),
    ("mon_start", "mon_end", "Monday", "2025-05-05"),
    ("tue_start", "tue_end", "Tuesday", "2025-05-06"),
    ("wed_start", "wed_end", "Wednesday", "2025-05-07"),
    ("thu_start", "thu_end", "Thursday", "2025-05-08"),
    ("fri_start", "fri_end", "Friday", "2025-05-09"),
    ("sat_start", "sat_end", "Saturday", "2025-05-10")
]

events = []

for start, end, day, dt in days:
    start_time = value_set(start)
    end_time = value_set(end)
    if start_time != "00:00:00" and end_time != "00:00:00":
        events.append({
            "title": f"{day}",
            "start": f"{dt}T{start_time}",
            "end":f"{dt}T{end_time}"
        })

st.subheader(f"Availability for {st.session_state['user']}")

calendar_options = {
    "headerToolbar" : {"left": "", "center": "", "right": ""},
    "initialView": "timeGridWeek",
    "initialDate": base_date,
    "allDaySlot": False,
    "events": events,
    "dayHeaderFormat": {"weekday":"long"}
}

calendar(events=events, options=calendar_options)

st.text("Monday")
mon_times = []
mon_start = st.time_input("Start", value=value_set("mon_start"), key="mon_start")
mon_end = st.time_input("End", value=value_set("mon_end"), key="mon_end")    

st.text("Tuesday")
tue_times = []
tue_start = st.time_input("Start", value=value_set("tue_start"), key="tue_start")
tue_end = st.time_input("End", value=value_set("tue_end"), key="tue_end")

st.text("Wednesday")
wed_times = []
wed_start = st.time_input("Start", value=value_set("wed_start"), key="wed_start")
wed_end = st.time_input("End", value=value_set("wed_end"), key="wed_end")

st.text("Thursday")
thu_times = []
thu_start = st.time_input("Start", value=value_set("thu_start"), key="thu_start")
thu_end = st.time_input("End", value=value_set("thu_end"), key="thu_end")

st.text("Friday")
fri_times = []
fri_start = st.time_input("Start", value=value_set("fri_start"), key="fri_start")
fri_end = st.time_input("End", value=value_set("fri_end"), key="fri_end")

st.text("Saturday")
sat_times = []
sat_start = st.time_input("Start", value=value_set("sat_start"), key="sat_start")
sat_end = st.time_input("End", value=value_set("sat_end"), key="sat_end")

st.text("Sunday")
sun_times = []
sun_start = st.time_input("Start", value=value_set("sun_start"), key="sun_start")
sun_end = st.time_input("End", value=value_set("sun_end"), key="sun_end")


if st.button("Submit"):
    data = {"id":st.session_state["id"], 
            "mon_start": mon_start.strftime("%H:%M:%S"), "mon_end": mon_end.strftime("%H:%M:%S"),
            "tue_start": tue_start.strftime("%H:%M:%S"), "tue_end": tue_end.strftime("%H:%M:%S"),
            "wed_start": wed_start.strftime("%H:%M:%S"), "wed_end": wed_end.strftime("%H:%M:%S"),
            "thu_start": thu_start.strftime("%H:%M:%S"), "thu_end": thu_end.strftime("%H:%M:%S"),
            "fri_start": fri_start.strftime("%H:%M:%S"), "fri_end": fri_end.strftime("%H:%M:%S"),
            "sat_start": sat_start.strftime("%H:%M:%S"), "sat_end": sat_end.strftime("%H:%M:%S"),
            "sun_start": sun_start.strftime("%H:%M:%S"), "sun_end": sun_end.strftime("%H:%M:%S"),
        }
    response = supabase.table("availability").upsert(data).execute()
    
    if response.data:
        st.success("Data added successfully!")
        response = supabase.table("availability").select("*").eq("id", st.session_state["id"]).single().execute()
        st.rerun()
    else:
        st.error("Error adding data!")

if st.button("Back"):
    st.switch_page("pages/calendar.py")

