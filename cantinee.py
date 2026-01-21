import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Page Setup ---
st.set_page_config(page_title="Canteen 2026", layout="wide")
DB_FILE = "orders.csv"  # This will act as our Excel sheet
MENU = {"Chicken Rice": 80, "Sambar Rice": 50, "Veg Burger": 60, "Coffee": 20}

# --- Sidebar ---
st.sidebar.title("🔐 Access Control")
role = st.sidebar.radio("Select View:", ["Student View", "Manager Login"])

# ---------------- STUDENT VIEW ----------------
if role == "Student View":
    st.title("🍽️ Order Food")
    with st.form("order_form", clear_on_submit=True):
        u_name = st.text_input("Name").replace(",", "")
        u_roll = st.text_input("Roll Number").replace(",", "")
        u_item = st.selectbox("Choose Item", list(MENU.keys()))
        
        if st.form_submit_button("Confirm Order"):
            if u_name and u_roll:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row = pd.DataFrame([[u_name, u_roll, u_item, MENU[u_item], now]], 
                                     columns=["Name", "Roll No", "Item", "Price", "Time"])
                
                # Save to the local virtual server file
                if not os.path.isfile(DB_FILE):
                    new_row.to_csv(DB_FILE, index=False)
                else:
                    new_row.to_csv(DB_FILE, mode='a', header=False, index=False)
                
                st.success(f"Order for {u_item} placed! Manager can see it now.")
                st.balloons()
            else:
                st.error("Please enter Name and Roll Number.")

# ---------------- MANAGER VIEW ----------------
else:
    st.title("👨‍🍳 Manager Dashboard")
    # Pull password from Streamlit Secrets (admin123)
    password = st.text_input("Enter Manager Password", type="password")
    
    if password == st.secrets["manager_password"]:
        st.success("Login Successful")
        
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            
            # Show summary
            st.subheader("📊 Kitchen Summary")
            summary = df.groupby("Item").size().reset_index(name='Count')
            st.table(summary)

            # Show the Excel Sheet
            st.subheader("📝 Order List")
            st.dataframe(df, use_container_width=True)
            
            # --- THE IMPORTANT PART: DOWNLOAD TO YOUR COMPUTER ---
            st.markdown("---")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Data to My System (Excel/CSV)",
                data=csv,
                file_name=f"canteen_orders_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.info("No orders found yet.")

