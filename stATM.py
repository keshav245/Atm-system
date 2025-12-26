import streamlit as st
import json
import os

# --- Configuration & Styling ---
st.set_page_config(page_title="Secure Bank System", page_icon="🏦")

# --- Database Logic ---
DB_FILE = "accounts.json"
ADMIN_USER = "keshav"
ADMIN_PASS = "514"

def load_data():
    if not os.path.exists(DB_FILE) or os.stat(DB_FILE).st_size == 0:
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None # 'admin' or 'user'
if "current_uid" not in st.session_state:
    st.session_state.current_uid = None

# --- UI Components ---

def logout():
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.current_uid = None
    st.rerun()

def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    st.write(f"Welcome, **{ADMIN_USER}**")
    
    with st.expander("➕ Create New Account"):
        new_id = st.text_input("New Account Number")
        new_pin = st.text_input("Set 4-Digit PIN", type="password")
        if st.button("Create Account"):
            data = load_data()
            if new_id in data:
                st.error("Account already exists!")
            elif new_id and new_pin:
                data[new_id] = {"pin": int(new_pin), "balance": 0}
                save_data(data)
                st.success(f"Account {new_id} created successfully!")
            else:
                st.warning("Please fill all fields.")

    if st.button("View All Accounts"):
        data = load_data()
        st.json(data)

    st.button("Logout", on_click=logout, type="primary")

def user_dashboard():
    uid = st.session_state.current_uid
    st.title(f"🏦 Welcome, ID: {uid}")
    
    data = load_data()
    balance = data[uid]["balance"]
    
    st.metric("Current Balance", f"${balance:,.2f}")

    col1, col2 = st.columns(2)
    
    with col1:
        dep_amt = st.number_input("Deposit Amount", min_value=0, step=100)
        if st.button("Deposit"):
            data[uid]["balance"] += dep_amt
            save_data(data)
            st.success("Deposit Successful!")
            st.rerun()

    with col2:
        with_amt = st.number_input("Withdraw Amount", min_value=0, step=100)
        if st.button("Withdraw"):
            if balance >= with_amt:
                data[uid]["balance"] -= with_amt
                save_data(data)
                st.success("Withdrawal Successful!")
                st.rerun()
            else:
                st.error("Insufficient Funds!")

    st.divider()
    st.button("Logout", on_click=logout)

# --- Main Routing ---

if not st.session_state.logged_in:
    st.title("🏛️ CENTRAL BANK")
    tab1, tab2 = st.tabs(["User Login", "Admin Login"])

    with tab1:
        u_id = st.text_input("Account ID")
        u_pin = st.text_input("PIN", type="password", key="u_pass")
        if st.button("Login as User"):
            data = load_data()
            if u_id in data and data[u_id]["pin"] == int(u_pin):
                st.session_state.logged_in = True
                st.session_state.user_type = "user"
                st.session_state.current_uid = u_id
                st.rerun()
            else:
                st.error("Invalid ID or PIN")

    with tab2:
        a_name = st.text_input("Admin Name")
        a_pin = st.text_input("Admin PIN", type="password", key="a_pass")
        if st.button("Login as Admin"):
            if a_name == ADMIN_USER and a_pin == ADMIN_PASS:
                st.session_state.logged_in = True
                st.session_state.user_type = "admin"
                st.rerun()
            else:
                st.error("Invalid Admin Credentials")

else:
    if st.session_state.user_type == "admin":
        admin_dashboard()
    else:
        user_dashboard()