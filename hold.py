# packages
import polars as pl
import plotly.express as px
import plotly.io as pio
import numpy as np
import pandas as pd
import datetime
from streamlit_calendar import calendar as st_calendar
import streamlit as st
from supabase import create_client, Client
import redis
import json

# Connect to redis database
r = redis.Redis(
    host='redis-11471.c114.us-east-1-4.ec2.redns.redis-cloud.com',
    port=11471,
    decode_responses=True,
    username="default",
    password="lSNF41TXrZKYt2K8OOUZ3Ib0BVq3Ft7h",
)

# Check if it worked
try:
    r.ping()
    print("Connected to Redis successfully!")
except redis.ConnectionError:
    print("Failed to connect to Redis.")

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])   

supabase = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query():
    response = supabase.table("mytable").select("*").execute()
    return response.data

if st.button("Sign Up"):
    st.switch_page("pages/add_user.py")
if st.button("Log In"):
    st.switch_page("pages/login.py")

# Create tabs for app
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Messaging", "Analytics", "Calandar"])

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {display: none !important;}
        button[kind="icon"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True
)

# Tab 1: Homepage
with tab1:
    st.header("main page")

# Tab 2: Messaging
with tab2:
    chat_rooms = ["Team", "Managers", "Announcements"]

    st.title("Chat Rooms")

    prompt = st.chat_input("Say Something")

    if prompt:
        if prompt.strip():
            message_data = {
                "message": prompt,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        r.lpush("messages", json.dumps(message_data))
        st.success("Message Sent")

    st.subheader("Message History")
        
    messages = r.lrange("messages", 0, 9)
    loaded_msg = [json.loads(msg) for msg in messages]
    loaded_msg.sort(key=lambda x: x["timestamp"])

    message_board_html = """
    <div style="
        display: flex; 
        flex-direction: column; 
        padding: 10px; 
        gap: 10px; 
        background-color: #FFFFFF;
        height: 400px;
        overflow-y: auto;
        border: 1px solid #ccc; 
        border-radius: 10px;
    ">
    """

    last_date = None
    
    for msg in loaded_msg:
        timestamp = datetime.datetime.fromisoformat(msg["timestamp"])
        msg_time = timestamp.strftime("%I:%M %p")  
        msg_date = timestamp.strftime("%B %d, %Y")

        if last_date != msg_date:
            message_board_html += f"<p style='font-size:12px; color:gray; text-align: center; margin-bottom: 5px;'>{msg_date}</p>"
            last_date = msg_date

        message_board_html += f"<p style='font-size: 12px; color: grey; margin: 0;'>{msg_time}</p>"

        message_board_html += f"""
        <div style="
            display: inline-block; 
            width: fit-content;
            max-width: 60%;
            padding: 10px; 
            border: 1px solid #ccc; 
            border-radius: 15px; 
            background-color: #7cc9f6;
            word-wrap: break-word;
            overflow-wrap: break-word;
            margin-bottom: 5px;
        ">
            <p style="font-size: 15px; color: black; margin: 0;">{msg['message']}</p>
        </div>
        """
    message_board_html += "</div>"

    st.markdown(message_board_html, unsafe_allow_html=True)

with tab3:
    st.header("Analytics Dashboard")
    st.write("Display charts, data, and insights here.")

    rows = run_query()

    # Print results.
    for row in rows:
        st.write(f"{row['name']} has a :{row['pet']}:")

with tab4:
    st.header("Calendar")
    calendar_options = {
    "editable": True,
    "selectable": True,
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "timeGridDay,timeGridWeek",
    },
    "slotMinTime": "06:00:00",
    "slotMaxTime": "18:00:00",
    "initialView": "timeGridWeek"
    }

    calendar_events = [
        {
            "title": "Event 1",
            "start": "2023-07-31T08:30:00",
            "end": "2023-07-31T10:30:00",
            "resourceId": "a",
        },
        {
            "title": "Event 2",
            "start": "2023-07-31T07:30:00",
            "end": "2023-07-31T10:30:00",
            "resourceId": "b",
        },
    ]

    st_calendar = st_calendar(
        events=calendar_events,
        options=calendar_options,
        key='calendar',
    )
    st.write(st_calendar)