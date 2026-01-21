import streamlit as st
import pandas as pd
from datetime import datetime
import os
import csv

# --- Basic Configuration ---
st.set_page_config(page_title="Campus Canteen Fresh Start", layout="wide")
DB_FILE = "orders.csv"
MENU = {"Chicken Rice": 80, "Sambar Rice": 50, "Veg Burger": 60, "Coffee": 20}

# --- Sidebar Navigation ---
st.sidebar.title("🔐 Access Control")
role = st.sidebar.radio("Select View:", ["Student View", "Manager Login"])

# ---------------- STUDENT VIEW ----------------
if role == "Student View":
    st.title("🍽️ Order Food")
    with st.form("order_form", clear_on_submit=True):
        u_name = st.text_input("Name").replace(",", "")  # Strip commas for CSV safety
        u_roll = st.text_input("Roll Number").replace(",", "")
        u_item = st.selectbox("Choose Item", list(MENU.keys()))
        
        if st.form_submit_button("Confirm Order"):
            if u_name and u_roll:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file_exists = os.path.isfile(DB_FILE)
                
                # Direct Write to ensure the file updates on D: drive
                with open(DB_FILE, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["Name", "Roll No", "Item", "Price", "Time"])
                    writer.writerow([u_name, u_roll, u_item, MENU[u_item], now])
                
                st.success(f"Order for {u_item} recorded! Your database is now active.")
                st.balloons()
            else:
                st.error("Please enter both Name and Roll Number.")

# ---------------- MANAGER VIEW ----------------
else:
    st.title("👨‍🍳 Manager Dashboard")
    password = st.text_input("Password", type="password")
    
    if password == "admin123":
        st.cache_data.clear()  # Clear memory to show new orders instantly
        
        # --- FRESH START FEATURE ---
        st.sidebar.markdown("---")
        if st.sidebar.button("🗑️ Reset All Data", help="Permanently delete all order history"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                st.sidebar.success("Database deleted! Website is fresh again.")
                st.rerun()  # Refresh the page
        
        # --- DATA DISPLAY ---
        if os.path.exists(DB_FILE):
            try:
                df = pd.read_csv(DB_FILE, on_bad_lines='skip')
                
                st.subheader("📊 Today's Summary")
                summary = df.groupby("Item").size().reset_index(name='Quantity')
                st.table(summary)

                st.subheader("📝 Live Order Excel Sheet")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error("The data file is corrupted. Click 'Reset All Data' in the sidebar to fix it.")
        else:
            st.info("The canteen is currently empty. No orders found.")