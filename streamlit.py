# %% [markdown]
# packages
import streamlit as st
import polars as pl
import plotly.express as px
import plotly.io as pio
import numpy as np
import pytz
import datetime
import pandas as pd
from streamlit_calendar import calendar as st_calendar

data = pd.read_csv("./global_poi.csv")

# %%
tab1, tab2, tab3 = st.tabs(["Home", "Analytics", "Calandar"])

# Content for each tab
with tab1:
    st.header("Welcome to the Home Tab")
    st.write("This is the home section.")
    st.write("welcome to my sped talk")

with tab2:
    st.header("Analytics Dashboard")
    st.write("Display charts, data, and insights here.")

    st.write(data)

with tab3:
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