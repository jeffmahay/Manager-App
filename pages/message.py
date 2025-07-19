import streamlit as st
import datetime
import json
from supabase import create_client
from landing import r

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]) 

supabase = init_connection()

# Navigation Bar
st.sidebar.page_link('pages/home.py', label='Home')
st.sidebar.page_link('pages/message.py', label='Messages')
st.sidebar.page_link('pages/calendar.py', label='Schedule')
st.sidebar.page_link('pages/chart.py', label='Statistics')

# Pull from login and chat room tables on supabase
emp_response = supabase.table("login").select("id", "first_name", "last_name").order("last_name").execute()
room_response = supabase.table("chat_rooms").select("*").execute()

# Configure data pull in dictionary so that user id isn't visible when called
employees = {
    f"{person['first_name']}, {person['last_name']}": person['id']
    for person in emp_response.data
}

st.title("Chat Rooms")

# Check if state exists and if it does, default to false
if 'show_room_form' not in st.session_state:
    st.session_state.show_room_form = False

# Only show create room button if user is manager. Button toggles form visibility
if st.session_state.get('type') in ["General Manager", "Assistant General Manager"]:
    if st.button("Create Room"):
        st.session_state.show_room_form = not st.session_state.show_room_form

# Container is always present, just not always rendered
with st.container():
    if st.session_state.show_room_form:
        # Form to send data to supabase
        with st.form(key="room_form"):
            name = st.text_input("Room Name")
            users = st.multiselect("Add People", list(employees.keys()))
            submit_button = st.form_submit_button('Submit')
            # Prep info for export to Supabase
            if submit_button:
                data = {
                    "room_name": name,
                    "users": users
                }
                # If room name isn't blank and has users in it
                if data["room_name"].strip() != "" and len(data["users"]) > 0:
                    try:
                        # upsert into supabase the chat room name and id
                        response = supabase.table("chat_rooms").upsert(data, on_conflict=["room_id"]).execute()
                        # if connection works, hide form and rerun
                        if response.data:
                            st.session_state.show_room_form = False
                            st.rerun()
                        else:
                            st.error("Error saving to database")
                    # Will display error message if cannot connect to supabase
                    except Exception as e:
                        st.error(f"Supabase error: {str(e)}")
                else:
                    st.error("Please Fill Out Form")

# Displays all rooms in nice style
## Note: Change room users to display latest message instead ##

    

for room in room_response.data:
    room_key = f"messages:{room['room_id']}"
    messages = r.lrange(room_key, 0, 0)
    if messages:
        try:
            message_data = json.loads(messages[0])
            latest_message = f"{message_data['user']}: {message_data['message']}"
        except (json.JSONDecodeError, KeyError) as e:
            latest_message = "Error parsing message"
    else:
        latest_message = "No messages yet"
    with st.form(f"{room['room_id']}"):
        st.markdown(
            f"""
            <div style='padding: 10px; border: 1px solid #ccc; border-radius: 10px; cursor: pointer;'>
                <strong>{room['room_name']}</strong><br>
                {latest_message}
            </div>
            """,
            unsafe_allow_html=True
        )
        # Button to display chat room
        submit = st.form_submit_button("Open")
        if submit:
            st.session_state.active_room = room['room_id']
            st.switch_page('pages/chat.py')