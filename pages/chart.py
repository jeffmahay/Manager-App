import streamlit as st
import pandas as pd
import altair as alt
from supabase import create_client
from datetime import datetime


@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]) 

supabase = init_connection()

# Navigation Bar
st.sidebar.page_link('pages/home.py', label='Home')
st.sidebar.page_link('pages/message.py', label='Messages')
st.sidebar.page_link('pages/calendar.py', label='Schedule')
st.sidebar.page_link('pages/chart.py', label='Statistics')

st.header("Analytics Dashboard")

if 'show_data' not in st.session_state:
    st.session_state.show_data = False

if st.session_state.get('type') in ["General Manager", "Assistant General Manager"]:
    if st.button("Add Data"):
        st.session_state.show_data = not st.session_state.show_data

with st.container():
    if st.session_state.show_data:
        with st.form(key="data_form"):
            date = datetime.now()
            format_date = date.strftime("%a %d")

            weather = st.number_input("Forecast Temp (in Fahrenheit)", min_value=-50.0, max_value=150.0, value=0.0, step=0.1)
            employee_num = st.number_input("Employees on Shift", min_value=0, step=1, placeholder="0")
            labor_costs = st.number_input("Labor Costs", min_value=0.0, step=0.01)
            total_rev = st.number_input("Total Revenue", min_value=0.0, step=0.01)
            num_trans = st.number_input("Total Transactions", min_value=0, step=1)
            food_cost = st.number_input("Food Costs", min_value=0.0, step=0.01)

            labor_percent = (labor_costs / total_rev * 100) if total_rev > 0 else 0.0
            net_profit = total_rev - (labor_costs + food_cost)

            submit_button = st.form_submit_button("Submit Data")

            if submit_button:
                try:
                    data = {
                        "date": format_date,
                        "weather": weather,
                        "num_employees": employee_num,
                        "labor_costs": labor_costs,
                        "total_revenue": total_rev,
                        "num_transactions": num_trans,
                        "food_costs": food_cost,
                        "labor_percent": labor_percent,
                        "net_profit": net_profit
                    }

                    response = supabase.table("store_data").upsert(data).execute()

                    if response.data:
                        st.success("Data added successfully!")
                    else:
                        st.error("Error adding data!")
                except Exception as e:
                    st.error(f"Database error: {str(e)}")

out_response = supabase.table("store_data").select("*").execute()

data = out_response.data
df = pd.DataFrame(data)

profit_chart = alt.Chart(df).mark_line().encode(
    x=alt.X('date:O', title="Date"),
    y=alt.Y('net_profit:Q', title='Net Profit')
).properties(
    width=600,
    height=400
)

num_emp_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('date:O', title="Date"),
    y=alt.Y('num_employees:Q', title="Employees on Shift")
).properties(
    width=600,
    height=400
)

num_cust_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('date:O', title="Date"),
    y=alt.Y('num_transactions:Q', title="Customers Serviced")
).properties(
    width=600,
    height=400
)

st.altair_chart(profit_chart, use_container_width=True)
st.altair_chart(num_emp_chart, use_container_width=True)
st.altair_chart(num_cust_chart, use_container_width=True)