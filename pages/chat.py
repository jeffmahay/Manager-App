import streamlit as st
from streamlit_autorefresh import st_autorefresh
import datetime
import json
from supabase import create_client, Client
from landing import r

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]) 

# Navigation Bar
st.sidebar.page_link('pages/home.py', label='Home')
st.sidebar.page_link('pages/message.py', label='Messages')
st.sidebar.page_link('pages/calendar.py', label='Schedule')
st.sidebar.page_link('pages/chart.py', label='Statistics')

# autorefresh every 2000ms or 2 seconds to search for a new message between sessions
# st autorefresh pushes the weight of constantly refreshing the script onto the browser instead of streamlit's servers
st_autorefresh(interval=2000, limit=None, key="refresh_key")


st.title("Chat Rooms")

# Create latest timestamp session
if "last_timestamp" not in st.session_state:
    st.session_state.last_timestamp = None

if "active_room" in st.session_state:
    room_id = st.session_state.active_room
    room_key = f"messages:{room_id}"

    #grab latest message
    latest_raw = r.lindex(room_key, 0)
    # if there is a latest message
    if latest_raw:
        # r.lindex returns a string, so we need to turn it back into a dictionary
        latest_msg = json.loads(latest_raw)
        # grab timestamp
        latest_timestamp = latest_msg.get("timestamp")
        # if the timestamp is different from the current timestamp (aka a new message) then set as new timestamp and rerun page
        if latest_timestamp != st.session_state.last_timestamp:
            st.session_state.last_timestamp = latest_timestamp
            st.rerun()

    prompt = st.chat_input("Say Something")

    # When a message is sent, send message, time and who sent it to redis and rerun
    if prompt:
        if prompt.strip():
            message_data = {
                "message": prompt,
                "timestamp": datetime.datetime.now().isoformat(),
                "user": st.session_state.get("user")
            }
        r.lpush(room_key, json.dumps(message_data))
        st.success("Message Sent")
        st.rerun()

    # Grab last 10 messages, set to dictionary and sort by time sent
    messages = r.lrange(room_key, 0, 9)
    loaded_msg = [json.loads(msg) for msg in messages]
    loaded_msg.sort(key=lambda x: x["timestamp"])

    # HTML to style chat box
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

    # Convert timestamp to seperate date and time, in format I want
    for msg in loaded_msg:
        timestamp = datetime.datetime.fromisoformat(msg["timestamp"])
        msg_time = timestamp.strftime("%I:%M %p")  
        msg_date = timestamp.strftime("%B %d, %Y")

        # Add date to message
        if last_date != msg_date:
            message_board_html += f"<p style='font-size:12px; color:gray; text-align: center; margin-bottom: 5px;'>{msg_date}</p>"
            last_date = msg_date

        # Add user's name to message
        message_board_html += f"<p style='font-size: 13px; color: black; margin: 0;'>{msg.get('user')}</p>"
        
        # Add message with box to chat box
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
        # Add time to message
        message_board_html += f"<p style='font-size: 12px; color: grey; margin: 0;'>{msg_time}</p>"
        

    message_board_html += "</div>"

    # render entire thing together
    st.markdown(message_board_html, unsafe_allow_html=True)

if st.button("Back"):
    st.switch_page('pages/message.py')