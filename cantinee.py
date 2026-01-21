import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- App Config ---
st.set_page_config(page_title="Secure Canteen App", layout="wide")
MENU = {"Chicken Rice": 80, "Sambar Rice": 50, "Veg Burger": 60, "Coffee": 20}

# Connect to Google Sheets using the URL from your TOML secrets
conn = st.connection("gsheets", type=GSheetsConnection)

role = st.sidebar.radio("View:", ["Student View", "Manager Login"])

# ---------------- STUDENT VIEW ----------------
if role == "Student View":
    st.title("🍽️ Order Food")
    with st.form("order_form", clear_on_submit=True):
        u_name = st.text_input("Name")
        u_roll = st.text_input("Roll Number")
        u_item = st.selectbox("Item", list(MENU.keys()))

        if st.form_submit_button("Confirm Order"):
            if u_name and u_roll:
                # Get current data, add new row, and upload
                df = conn.read(ttl=0)
                new_data = pd.DataFrame([[u_name, u_roll, u_item, MENU[u_item], datetime.now().strftime("%Y-%m-%d %H:%M")]],
                                       columns=["Name", "Roll No", "Item", "Price", "Time"])
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(data=updated_df)
                st.success("Order Placed Successfully!")
            else:
                st.error("Fill all fields")

# ---------------- MANAGER VIEW ----------------
else:
    st.title("👨‍🍳 Manager Login")
    user_input = st.text_input("Enter Password", type="password")

    # This line checks the TOML secret, keeping your password hidden from GitHub!
    if user_input == st.secrets["manager_password"]:
        st.success("Welcome back!")
        data = conn.read(ttl=0)
        st.dataframe(data, use_container_width=True)
    elif user_input != "":
        st.error("Wrong Password")
