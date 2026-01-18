import streamlit as st
from models.Upload_CSV import Upload_CSV
from packetProcessor import PacketProcessor
from Database.DatabaseManager import DatabaseManager
from streamlit_option_menu import option_menu
from DashboardVisualizer import DashboardVisualizer
from anomaly_detection import AnomalyDetection
from settings import SettingsPage

class NetworkAnomalyApp:
    
    def __init__(self):
        st.set_page_config(layout="wide") 
        
        self.start_session()
        self.tooglebox = st.empty()
        
        with st.sidebar:
            st.markdown("## 📡 Packet Sniffing Controls")
            
            # Download CSV button
            if st.button("⬇️ Download CSV", use_container_width=True):
                self.dbmanager = DatabaseManager(dbname='network_anomaly', user='postgres', password='postgres')
                self.dbmanager.convert_to_csv()
                st.success("CSV exported successfully!")
            
            
            self.toggle()
            
        self.run()
        
    def toggle(self):
            toggle = st.toggle("Sniffing on")
            # print("Toggle",toggle)  
            
            if toggle:
                print("Toggle",toggle)
                self.processor.start_sniffing()
                # self.create_column()
                
            else:
                print("Toggle",toggle)
                self.processor.stop_sniffing()

                
    def start_session(self):
          # Session started
        if 'open_port' not in st.session_state:
            st.session_state.open_port = None
            st.session_state.active_connections_avg = None
            st.session_state.cpu_usage = None
            st.session_state.memory_usage = None
            st.session_state.packet_count = None
        
        if 'start_sniffing' not in st.session_state:
            st.session_state.start_sniffing = None
        
        if 'stop_sniffing' not in st.session_state:
            st.session_state.stop_sniffing = None
            
        if "processor" not in st.session_state:
            st.session_state.processor = PacketProcessor()
        self.processor = st.session_state.processor
        
        if "metrics_box" not in st.session_state:
            st.session_state.metrics_box = st.empty()
            
        if "cpu_box" not in st.session_state:
            st.session_state.cpu_box = st.empty()
        
        if "mem_box" not in st.session_state:
            st.session_state.mem_box = st.empty()
            
        if "active_box" not in st.session_state:
            st.session_state.active_box = st.empty()
            
        if "stack_area" not in st.session_state:
            st.session_state.stack_area = st.empty()
        
        if "process_metrics" not in st.session_state:
            st.session_state.process_metrics = st.empty()
        
        if "highlight" not in st.session_state:
            st.session_state.highlight = st.empty()
            
        if "records" not in st.session_state:
            st.session_state.records = []   
  
    def run(self):
        print("Running sidebar")
        with st.sidebar:
            selected = option_menu(
                "H-NIDS Main Menu", 
                [
                    "🏠 Dashboard",
                    "🚨 Alerts",
                    "⚙️ Settings"
                ],
                icons=[
                    "house",    # Dashboard
                    "bell",     # Alerts
                    "gear"      # Settings
                ],
                default_index= 0  # start with Dashboard
            )
        
        if selected == "🏠 Dashboard":
            self.home()  
        elif selected == "🚨 Alerts":
            self.anomaly_detection()  
        elif selected == "⚙️ Settings":
            self.settings() 
        else:
            st.write("Page not found")

            
            
    def home(self): 
        print("home")
        # if 'dashboard' not in st.session_state:
        #     st.session_state.dashboard = DashboardVisualizer()
        
        # self.dashboard = st.session_state.dashboard
        DashboardVisualizer()
        
            
    def anomaly_detection(self):    
        AnomalyDetection()
        
    
    def settings(self):
        sp = SettingsPage()
        sp.render()
            

if __name__ == "__main__":
    app = NetworkAnomalyApp()
