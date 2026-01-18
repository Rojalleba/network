import streamlit as st
import sys, os

# add parent folder (network) to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Database.DatabaseManager import DatabaseManager

class LoginApp:
    def __init__(self):
        # You can replace this with a database later
        self.dbManager = DatabaseManager(dbname="network_anomaly",user="postgres",password="postgres")

        # Initialize session state
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if "username" not in st.session_state:
            st.session_state.username = ""

    def login(self, username, password):
        """Authenticate the user."""
        validation = self.dbManager.validate_user(username,password)
        if validation == True:
            # Go to home
            print(f"{username} and {password} is available")
            return True
        return print(f"{username} and {password} is not available")

    def show_login_page(self):
        """Render the login form."""
        st.markdown(
            """
            <h2 style='text-align:center;'>🛡️ Network Anomaly Detection System</h2>
            <p style='text-align:center;'>Login to continue</p>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Username")
            password = st.text_input("🔒 Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if self.login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"✅ Welcome {username}!")
                else:
                    st.error("❌ Invalid username or password")




