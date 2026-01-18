import streamlit as st
import pandas as pd
from packetProcessor import PacketProcessor
import time
from kafka import KafkaProducer, KafkaConsumer
import json
from datetime import datetime
from Components.Line_Chart import LineChart
from windowAggregator import WindowAggregator
from compute_features import compute_features
from Database.DatabaseManager import DatabaseManager
from Components.StackAreaChart import StackAreaChart
import joblib

class DashboardVisualizer:
    def __init__(self):      
        st.set_page_config(page_title="Network Traffic Analysis",layout="wide")
        print("Dashboard1")
        self.memory_usage = None
        self.active_conn = None
        self.cpu_usage = None
        self.open_port = None
        
        # Fetch from DB
        
        self.start_session()
        
        self.database = st.session_state.database
        
        # Using offline container
        self.title = st.empty()
        self.mem_container = st.empty()
        self.cpu_container = st.empty()
        self.active_container = st.empty()
        self.stack_container = st.empty()
        
        self.offline_chart()
 
        data = []
        packet_list = []
        self.window_size=5
        self.last_window_time = datetime.now()
        
 
        consumer = KafkaConsumer(
            'packets-topic',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='latest',
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        aggregator = WindowAggregator()
        
        records = []
        anomalyRecords = []
        
        # Object Init
        line_chart_mem = LineChart(title="MEM_avg vs Window_Start")
        line_chart_cpu = LineChart(title="CPU_avg vs Window_Start")
        line_chart_active = LineChart(title="Acitve_Conn vs Window_Start")
        stack_area_chart = StackAreaChart()
        
        #  Settings config
        model_name = st.session_state.selected_model
    
        model = joblib.load("IsolationForest_model.pkl")
        
        if model_name == "IsolationForest":
        # Load the model
            model_path = "process_model/process_iso_forest_model.pkl"
            process_model = joblib.load(model_path)
        
        elif model_name == "OneClassSVM":
            model_path = "process_model/process_ocsvm_model.pkl"
            process_model = joblib.load(model_path)
        
        elif model_name == "DBSCAN":
            model_path = "process_model/process_dbscan_model.pkl"
            process_model = joblib.load(model_path)
    
        # Main loop over here
        for message in consumer: 
                self.title = st.empty()
                self.mem_container = st.empty()
                self.cpu_container = st.empty()
                self.active_container = st.empty()
                self.stack_container = st.empty()
                
                packet = message.value
                aggregator.add_packet(packet)
                
                filter_process = self.filter_process(packet)
                process_prediction = process_model.predict(filter_process)
                packet["anomaly"] = process_prediction
                score = float(process_model.decision_function(filter_process)[0]) # real score

                packet["anomaly"] = int(process_prediction)
                packet["score"] = score
                packet["severity"] = self.calculate_severity(score)
                    
                print("\nPacket",packet)
                
                # Append packet to the list
                packet_list.append(packet)  
                st.session_state.alerts.append(packet)
                
                with st.session_state.process_metrics:
                    self.create_table(packet_list)
                
                
                if aggregator.window_ready():
                    # Reupdate the session value
                    self.memory_usage = st.session_state.memory_usage
                    self.active_conn = st.session_state.active_connections_avg
                    self.cpu_usage = st.session_state.cpu_usage
                    self.open_port = st.session_state.open_port
                    self.packet_count = st.session_state.packet_count
                
                    
                    self.create_metrics()
                    
                    features = compute_features(aggregator.window_packets)
                    # self.database.insert_new_traffic(features)
                    
                    print("\nWINDOW FEATURES →")
                    print("WindowFeature",type(features))
                    
                    features_df = pd.DataFrame([features])
                    
                    print("After Window Feature\n",type(features_df))
                    
                    X_ready, cleanDf = self.filter_features(features_df)
                    
                    
                    
                    predictions = model.predict(X_ready)
                    cleanDf["anomaly"] = predictions
                    
                    print("singleCleanDF",cleanDf)
                    
                    # features rakhi rako for Argument
                    
                    self.update_session(features)
                    
                    cleanDf= cleanDf.drop(columns=["window_start","window_end","packet_count","interarrival_var","packet_size_variance","syn_ack_ratio","is_cloud_service"])
                    
                    anomalyRecords.append(cleanDf)
                    
                    anomalyDf = pd.concat(anomalyRecords, ignore_index=True)
                    
                    records.append(features)
                    
                    # Storing into the session
                    st.session_state.records.append(features)
                    
                    df = pd.DataFrame(records)
                    df["time_seconds"] = (df["window_start"] - df["window_start"].iloc[0]).dt.total_seconds()
                    
                    plot_df = df[["window_start", "mem_avg"]]
                    plot_cpu = df[["window_start","cpu_avg"]]
                    plot_active = df[["window_start","active_connections_avg"]]
                    
                    # with st.session_state.highlight:
                    #     self.highlighted_table(anomalyDf)
                    
                    with st.session_state.cpu_box:
                        line_chart_mem.render(plot_df,"window_start","mem_avg")
                    
                    with st.session_state.mem_box:
                        line_chart_cpu.render(plot_cpu,"window_start","cpu_avg")
                    
                    with st.session_state.active_box:
                        line_chart_active.render(plot_active,"window_start","active_connections_avg")
                    
                    
                    with st.session_state.stack_area:
                        stack_area_chart.render(df)
                        
                    # Reset for next window
                    aggregator.reset_window()
                    
                    
                packet['timestamp'] = pd.to_datetime(packet['timestamp'])
                
                
                # placeholder.dataframe(data[-5:])
        
        
        
    def update_session(self,features):
        st.session_state.open_port = int(features["open_ports_count"])
        st.session_state.active_connections_avg = int(features["active_connections_avg"])
        st.session_state.cpu_usage = int(features["cpu_avg"])
        st.session_state.memory_usage = int(features["mem_avg"])
        st.session_state.packet_count = int(features['packet_count'])
 
    def create_metrics(self): 
        with st.session_state.metrics_box:       
            row1_col1, row1_col2, row1_col3 = st.columns(3)
            
            row1_col1.metric("Total Packets Monitored", self.packet_count)
            row1_col2.metric("Total Alerts (Last 5 min)", self.packet_count)
            row1_col3.metric("CPU Usage (%)", self.cpu_usage)

            # Second row: 3 metrics horizontally
            row2_col1, row2_col2, row2_col3 = st.columns(3)
            
            row2_col1.metric("Memory Usage (%)", self.memory_usage)
            row2_col2.metric("Active Connections", self.active_conn)
            row2_col3.metric("Open Ports Count", self.open_port)

    def toggle(self):
            toggle = st.toggle("Sniffing on")
            # print("Toggle",toggle)  
            
            if toggle:
                print("Toggle",toggle)
                self.processor.start_sniffing()
                
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

        if "alerts" not in st.session_state:
            st.session_state.alerts = []
        
        if "selected_model" not in st.session_state:
            st.session_state.selected_model = "IsolationForest"  # default
            
        if "severity_critical" not in st.session_state:
            st.session_state.severity_critical = -0.30
            
        if "severity_warning" not in st.session_state:
            st.session_state.severity_warning = -0.10
            
        if "alerts" not in st.session_state:
            st.session_state.alerts = []
            
        if "processor" not in st.session_state:
            st.session_state.processor = PacketProcessor()
        self.processor = st.session_state.processor
        
        if "metrics_box" not in st.session_state:
            st.session_state.metrics_box = st.empty()
            
        if "process_metrics" not in st.session_state:
            st.session_state.process_metrics = st.empty()
        
        if "highlight" not in st.session_state:
            st.session_state.highlight = st.empty()
            
        if "cpu_box" not in st.session_state:
            st.session_state.cpu_box = st.empty()
        
        if "mem_box" not in st.session_state:
            st.session_state.mem_box = st.empty()
            
        if "active_box" not in st.session_state:
            st.session_state.active_box = st.empty()
            
        if "stack_area" not in st.session_state:
            st.session_state.stack_area = st.empty()
            
        if "records" not in st.session_state:
            st.session_state.records = []
            
        
            
        # Init database
        if "database" not in st.session_state:
            st.session_state.database = DatabaseManager(dbname="network_anomaly",user="postgres",password="postgres")
        
    def filter_features(self, features):
        numeric_features = [
            'packet_count','interarrival_var','packet_size_variance','syn_ack_ratio',
            'connection_duration','bytes_forward','bytes_backward',
            'cpu_avg','mem_avg','active_connections_avg','open_ports_count'
        ]

        categorical_features = ['is_cloud_service']  # binary
        
        print("Feature section",type(features))    
        # Remove NaN
        df = features.dropna()
        

        # Load scaler
        scaler = joblib.load("scalar.pkl")

        print("Feature data\n",df[numeric_features])
        
        # Scale ONLY numeric features (using transform)
        X_scaled = scaler.transform(df[numeric_features])

        # Combine numeric + categorical
        import numpy as np
        X = np.hstack([
            X_scaled,
            df[categorical_features].values
        ])

        return X, df
   
    def offline_chart(self):   
        try: 
            line_chart_mem = LineChart(title="MEM_avg vs Window_Start")
            line_chart_cpu = LineChart(title="CPU_avg vs Window_Start")
            line_chart_active = LineChart(title="Acitve_Conn vs Window_Start")
            stack_area_chart = StackAreaChart()
                
            records = self.database.get_last_ten()
            print("REcords")
            
            if records is None:
                st.warning("No records found.")
            
            df = pd.DataFrame(records)
            df["time_seconds"] = (df["window_start"] - df["window_start"].iloc[0]).dt.total_seconds()
                        
            plot_df = df[["window_start", "mem_avg"]]
            plot_cpu = df[["window_start","cpu_avg"]]
            plot_active = df[["window_start","active_connections_avg"]]
            
            with self.title:
                st.header("Database Logs")
            
            with self.mem_container:
                line_chart_mem.render(plot_df,"window_start","mem_avg")
                        
            with self.cpu_container:
                line_chart_cpu.render(plot_cpu,"window_start","cpu_avg")
                        
            with self.active_container:
                line_chart_active.render(plot_active,"window_start","active_connections_avg")
                        
                        
            with self.stack_container:
                stack_area_chart.render(df)        
        
        except Exception as e:
            print("Exception",e)
                  
    def highlight_columns(self,val, column_name):
        if column_name == 'anomaly' and val == -1:
            return 'background-color: #ff4b4b; color: white; font-weight:bold'
        return ''

    def highlighted_table(self, df):
        if df.empty:
            st.write("No anomaly records yet.")
            return
        
        st.subheader("Anomaly Table (Only 'Anomaly' Column Highlighted)")
        
        st.dataframe(
            df.style.applymap(
                lambda val: self.highlight_columns(val, 'anomaly'),
                subset=['anomaly']
            )
        )

    def filter_process(self,features):
        numeric_features = ['size', 'ttl', 'cpu_percent', 'mem_percent', 'active_connections']
        binary_cols = ['syn_flag', 'fin_flag', 'ack_flag']
        
        # Load scaler
        model_path = "process_model/process_scaler_model.pkl"
        scaler = joblib.load(model_path)
        
        if isinstance(features, dict):
            features = pd.DataFrame([features])
            
        if features.shape[0] == 0:
        # No rows left after filtering
            print("No valid process data to scale.")
            return features  
        
        # Scale ONLY numeric features (using transform)
        X_scaled = scaler.transform(features[numeric_features])
        
        # Combine numeric + categorical
        import numpy as np
        X = np.hstack([
            X_scaled,
            features[binary_cols].values
        ])
        
        return X
    
    def create_table(self,df_packets):
        df_packets = pd.DataFrame(df_packets)
        df_packets = df_packets.drop(columns=["ttl","syn_flag","fin_flag","ack_flag",])
    # Optional: readable label for anomaly
        df_packets['anomaly_label'] = df_packets['anomaly'].replace({1: 'Normal', -1: 'Anomaly'})

    # Function to highlight anomalies in red
        def highlight_anomaly(val):
            if val == -1:
                return 'background-color: red; color: white'
            return ''

        # Display the table
        st.dataframe(df_packets.style.applymap(highlight_anomaly, subset=['anomaly']))
        
    def calculate_severity(self, score):
        critical_threshold = st.session_state.severity_critical
        warning_threshold = st.session_state.severity_warning
        
        if score < critical_threshold:
            return "critical"
        elif score < warning_threshold:
            return "warning"
        else:
            return "low"