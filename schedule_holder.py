# supabase = init_connection()

# response = supabase.table("login").select("id", "first_name", "last_name").order("last_name").execute()

# employees = {
#     f"{person['last_name']}, {person['first_name']}": person['id']
#     for person in response.data
# }

# employees = {"-- Select an employee --": None, **employees}

# selected = st.selectbox("Employees", employees, index=0)

# if selected != "-- Select an employee --":
#     selected_id = employees[selected]

#     try:
#         response = supabase.table("availability").select("*").eq("id", selected_id).single().execute()
#         data = response.data
#     except Exception:
#         data = None
    
#     if data == None:
#         st.error("No data for employee. Please have them set availability")
#     else:
#         def value_set(day):
#             # day variable would be the columns in the availability table in supabase
#             # ex: mon_start
#             if data[day] != None:
#                 return data[day]
#             else:
#                 return None

#         base_date = "2025-05-04"
#         days = [
#             ("sun_start", "sun_end", "Sunday", "2025-05-04"),
#             ("mon_start", "mon_end", "Monday", "2025-05-05"),
#             ("tue_start", "tue_end", "Tuesday", "2025-05-06"),
#             ("wed_start", "wed_end", "Wednesday", "2025-05-07"),
#             ("thu_start", "thu_end", "Thursday", "2025-05-08"),
#             ("fri_start", "fri_end", "Friday", "2025-05-09"),
#             ("sat_start", "sat_end", "Saturday", "2025-05-10")
#         ]

#         events = []

#         for start, end, day, dt in days:
#             start_time = value_set(start)
#             end_time = value_set(end)
#             if start_time != "00:00:00" and end_time != "00:00:00":
#                 events.append({
#                     "title": f"{day}",
#                     "start": f"{dt}T{start_time}",
#                     "end":f"{dt}T{end_time}"
#                 })

#         st.subheader(f"Availability for {selected}")

#         calendar_options = {
#             "headerToolbar" : {"left": "", "center": "", "right": ""},
#             "initialView": "timeGridWeek",
#             "initialDate": base_date,
#             "allDaySlot": False,
#             "events": events,
#             "dayHeaderFormat": {"weekday":"long"}
#         }

#         calendar(events=events, options=calendar_options)