import streamlit as st
import pandas as pd
import re
from supabase import create_client
from streamlit_calendar import calendar
from streamlit_datetime_range_picker import datetime_range_picker


# Navigation Bar
st.sidebar.page_link('pages/home.py', label='Home')
st.sidebar.page_link('pages/message.py', label='Messages')
st.sidebar.page_link('pages/calendar.py', label='Schedule')
st.sidebar.page_link('pages/chart.py', label='Statistics')

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]) 


st.header('Schedule')

supabase = init_connection()

response = supabase.table("login").select("id", "first_name", "last_name").order("last_name").execute()

employees = {
    f"{person['last_name']}, {person['first_name']}": person['id']
    for person in response.data
}

data = [
    {
        "Employee": f"{person['last_name']}, {person['first_name']}",
        "Monday": " ",
        "Tuesday": " ",
        "Wednesday": " ",
        "Thursday": " ",
        "Friday": " ",
        "Saturday": " ",
        "Sunday": " "
    }
    for person in response.data
]

df = pd.DataFrame(data)

edited_df = st.data_editor(
    df,
    column_config = {
        "day": st.column_config.TextColumn(
            day,
            help = "Enter time range in format 'start - end' (eg; '1 - 10')"
        )
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]    
    },
    disabled = ["Employee"],
    hide_index = True,
    key = "data_editor"
)

if st.button("Save"):
    valid = True
    errors = []
    schedule_data = []
    pattern = r"^\d+\s*-\s*\d+$"

    for index, row in edited_df.iterrows():
        employee_name = row["Employee"]
        if employee_name not in employees:
            valid = False
            errors.append(f"Employee {employee_name} not found in database.")
            continue
        try:
            last_name, first_name = employee_name.split(", ")
        except ValueError:
            valid = False
            errors.append(f"Invalid employee name format for {employee_name}.")
            continue
        employee_id = employees[employee_name]

        employee_dat = {
            "id": employee_id,
            "first_name": employee_name.split(", ")[1],
            "last_name": employee_name.split(", ")[0],
            "Monday": "",
            "Tuesday": "",
            "Wednesday": "",
            "Thursday": "",
            "Friday": "",
            "Saturday": "",
            "Sunday": ""
        }

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            value = row[day]
            if value and value.strip():
                if not re.match(pattern, value):
                    valid = False
                    errors.append(f"Invalid input for {row['Employee']} on {day}: Must be in format 'start - end' (e.g., '1 - 10').")
                else:
                    employee_dat[day] = value

        schedule_data.append(employee_dat)

    if valid:
        if schedule_data:
            try:
                response = supabase.table("schedule").upsert(schedule_data, on_conflict=["id"]).execute()
                if response.data:
                    st.success("Saved to database")
                else:
                    st.error("Error saving to database")
            except Exception as e:
                st.error(f"Supabase error: {str(e)}")
        else:
            st.warning("No valid data to save")
    else:
        for error in errors:
            st.error(error)


st.subheader("Availability")
employees = {"-- Select an employee --": None, **employees}

selected = st.selectbox("Employees", employees, index=0)

if selected != "-- Select an employee --":
    selected_id = employees[selected]

    try:
        response = supabase.table("availability").select("*").eq("id", selected_id).single().execute()
        data = response.data
    except Exception:
        data = None
    
    if data == None:
        st.error("No data for employee. Please have them set availability")
    else:
        def value_set(day):
            # day variable would be the columns in the availability table in supabase
            # ex: mon_start
            if data[day] != None:
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

        st.subheader(f"Availability for {selected}")

        calendar_options = {
            "headerToolbar" : {"left": "", "center": "", "right": ""},
            "initialView": "timeGridWeek",
            "initialDate": base_date,
            "allDaySlot": False,
            "events": events,
            "dayHeaderFormat": {"weekday":"long"}
        }

        calendar(events=events, options=calendar_options)        



if st.button("Back"):
    st.switch_page('pages/calendar.py')
