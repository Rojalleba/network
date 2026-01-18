import streamlit as st
from datetime import datetime

class SettingsPage:

    def __init__(self):
        """
        Initialize settings and make sure defaults are stored in session_state
        """
        # Default thresholds
        if "contamination" not in st.session_state:
            st.session_state.contamination = 0.05
        if "severity_critical" not in st.session_state:
            st.session_state.severity_critical = -0.30
        if "severity_warning" not in st.session_state:
            st.session_state.severity_warning = -0.10

        # Default model selection
        if "selected_model" not in st.session_state:
            st.session_state.selected_model = "IsolationForest"

        # Model metadata (example, can update dynamically)
        if "model_info" not in st.session_state:
            st.session_state.model_info = {
                "name": "IsolationForest",
                "trained_on": "2025-11-20",
                "features": ["size", "ttl", "port", "syn_flag"],
                "n_estimators": 100
            }

    def render(self):
        """
        Render the settings page
        """
        st.title("⚙️ Settings")
        st.write("Configure model and threshold parameters for anomaly detection")

        st.markdown("### 🔹 Threshold Settings")
        self.render_threshold_settings()

        st.markdown("### 🔹 Model Selection")
        self.render_model_selection()

        st.markdown("### 🔹 Model Information")
        self.render_model_info()

    # -------------------------------
    # Threshold Settings
    # -------------------------------
    def render_threshold_settings(self):
        st.session_state.severity_critical = st.slider(
            "Critical Severity Threshold",
            min_value=-1.0,
            max_value=0.0,
            value=st.session_state.severity_critical,
            step=0.01
        )

        st.session_state.severity_warning = st.slider(
            "Warning Severity Threshold",
            min_value=-1.0,
            max_value=0.0,
            value=st.session_state.severity_warning,
            step=0.01
        )

    # -------------------------------
    # Model Selection
    # -------------------------------
    def render_model_selection(self):
        st.session_state.selected_model = st.selectbox(
            "Choose Detection Model",
            ["IsolationForest", "OneClassSVM", "DBSCAN"],
            index=["IsolationForest", "OneClassSVM", "DBSCAN"].index(st.session_state.selected_model)
        )

    # -------------------------------
    # Model Information Display
    # -------------------------------
    def render_model_info(self):
        info = st.session_state.model_info
        st.text(f"Model Name: {info.get('name', 'N/A')}")
        st.text(f"Trained On: {info.get('trained_on', 'N/A')}")
        st.text(f"Features Used: {', '.join(info.get('features', []))}")

        # Optional extra info
        if "n_estimators" in info:
            st.text(f"Number of Trees: {info['n_estimators']}")
