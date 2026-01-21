import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Canteen 2026", layout="wide")

# Menu and Prices
MENU = {
    "Chicken Rice": 80,
    "Sambar Rice": 50,
    "Veg Burger": 60,
    "Coffee": 20
}

# --- Connect to Google Sheets ---
# This uses the [connections.gsheets] from your Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- Sidebar Navigation ---
st.sidebar.title("🔐 Access Control")
role = st.sidebar.radio("Select View:", ["Student View", "Manager Login"])

# ---------------- STUDENT VIEW ----------------
if role == "Student View":
    st.title("🍽️ Place Your Order")
    
    with st.form("order_form", clear_on_submit=True):
        u_name = st.text_input("Full Name").replace(",", "")
        u_roll = st.text_input("Roll Number").replace(",", "")
        u_item = st.selectbox("Select Item", list(MENU.keys()))

        st.info(f"Amount to Pay: ₹{MENU[u_item]}")
        submitted = st.form_submit_button("Confirm & Order")

        if submitted:
            if u_name and u_roll:
                try:
                    # 1. Read existing data from Google Sheets
                    existing_data = conn.read(ttl=0)
                    
                    # 2. Prepare new row
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_row = pd.DataFrame([{
                        "Name": u_name,
                        "Roll No": u_roll,
                        "Item": u_item,
                        "Price": MENU[u_item],
                        "Time": now
                    }])

                    # 3. Add new row to existing data and update Google Sheet
                    updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                    conn.update(data=updated_df)

                    st.success(f"Order for {u_item} recorded in Google Sheets!")
                    st.balloons()
                except Exception as e:
                    st.error("Connection Error: Make sure your Google Sheet is set to 'Anyone with link can Edit'")
            else:
                st.warning("Please enter your Name and Roll Number.")

# ---------------- MANAGER VIEW ----------------
else:
    st.title("👨‍🍳 Manager Dashboard")
    
    # This pulls 'manager_password' from your Streamlit Secrets TOML
    password_attempt = st.text_input("Enter Manager Password", type="password")

    if password_attempt == st.secrets["manager_password"]:
        st.success("Access Granted")
        
        # Pull fresh data from Google Sheets
        df = conn.read(ttl=0)

        if not df.empty:
            # Summary View
            st.subheader("📊 Today's Preparation Summary")
            summary = df.groupby("Item").size().reset_index(name='Quantity')
            st.table(summary)

            # Full Order View
            st.subheader("📝 Live Order List (Excel View)")
            st.dataframe(df, use_container_width=True)

            # Download Button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Excel (CSV)", data=csv, file_name="canteen_orders.csv")
        else:
            st.info("No orders found in Google Sheets yet.")

    elif password_attempt != "":
        st.error("Incorrect Password")
