import streamlit as st
import redis
from supabase import create_client, Client

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




st.title("Welcome")


if st.button("Sign In"):
    st.switch_page("pages/login.py")

if st.button("Sign Up"):
    st.switch_page("pages/add_user.py")
