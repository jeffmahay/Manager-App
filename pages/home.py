# packages
import streamlit as st
import json
import datetime
from landing import r

# Navigation Bar
st.sidebar.page_link('pages/home.py', label='Home')
st.sidebar.page_link('pages/message.py', label='Messages')
st.sidebar.page_link('pages/calendar.py', label='Schedule')
st.sidebar.page_link('pages/chart.py', label='Statistics')

st.header("Home")

if st.button("Sign Out"):
    st.session_state.clear()
    st.switch_page("landing.py")

if 'user' in st.session_state:
    st.subheader(f"Welcome, {st.session_state['user']}")
    st.subheader(f"You are currently signed in as a {st.session_state['type']}")
else:
    st.error("Please log in first.")
    st.switch_page("landing.py")

st.subheader("Anouncements")

if "show_form" not in st.session_state:
    st.session_state.show_form = False

form_placeholder = st.empty()

if st.session_state.get('type') in ["General Manager", "Assistant General Manager"]:
    if st.button("Post/Close"):
        st.session_state.show_form = not st.session_state.show_form
        

if st.session_state.show_form:
    with form_placeholder.container():
        with st.form(key="announcement_form"):
            title = st.text_input("Title:")
            message = st.text_area("Details:")
            submit_button = st.form_submit_button(label="Submit")

            # push message to redis
            if submit_button:
                announce_data = {
                    "title": title,
                    "message": message,
                    "user": st.session_state['user'],
                    "timestamp": datetime.datetime.now().isoformat()
                }
                r.lpush("announcements", json.dumps(announce_data))
                st.success("Message Sent")

                st.session_state.show_form = False
                st.rerun()


# pull last 10 messages from redis, load in json and sort by date
announcements = r.lrange("announcements", 0, 1)

loaded_ann = [json.loads(ann) for ann in announcements]

for ann in loaded_ann:
    timestamp = datetime.datetime.fromisoformat(ann["timestamp"])
    ann_time = timestamp.strftime("%I:%M %p")  
    ann_date = timestamp.strftime("%B %d, %Y")

    st.subheader(ann["title"])
    st.markdown(f"Posted by {ann['user']}")
    st.markdown(f"{ann_date}")
    st.markdown(ann["message"])

    st.markdown(f"*Posted at {ann_time}*")
