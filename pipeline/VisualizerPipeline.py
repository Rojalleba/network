from Database.DatabaseManager import DatabaseManager
from Visualizer.Visualizer import DataTableVisualizer
from sklearn.preprocessing import StandardScaler
import joblib
import streamlit as st
import pandas as pd
import plotly.express as px
from Components.Barchart import Barchart
from Components.ScatterPlot import ScatterPlot
from Components.Table import Table
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
from features import SELECTED_FEATURES

class VisualizerPipeline:    
    def __init__(self,model_path):
        self.model_path = model_path
        self.data = None
        self.model = joblib.load(self.model_path)
        self.scaler = StandardScaler()
        
        # Container
        self.scatterplotA_placeholder = st.empty()
        self.barchart_placeholder = st.empty()
        self.scatterplotB_placeholder = st.empty()
        self.table_placeholder = st.empty()
            
    def Predict_Anomaly(self,df):
        df = df.reset_index(drop=True)

        df = df.copy()
        filter_df = df.drop(columns=['Protocol', 'source', 'destination', 'avg_size','packet_count', 'PacketsSent', 'PacketsReceived', 'BytesSent', 'BytesReceived', 'avg_ttl', 'syn_count', 'fin_count', 'ack_count', 'first_ts', 'last_ts'])
        
        print("From Predict_Anomaly fiter data frame \n",filter_df)
    
    
    def _VisualizeData(self,df):
        df = df.sort_values(by=["BytesSent"],ascending = False).head(30)
        
        # Placing inside container
        with self.barchart_placeholder.container():
            Barchart(df,"source","BytesSent",title="Bar Chart")    
        
        with self.scatterplotA_placeholder.container():            
            ScatterPlot(df,"BytesSent","BytesReceived","source","source")
        
        with self.scatterplotB_placeholder.container():
            ScatterPlot(df,"PacketsSent","PacketsReceived","source","source")
        
        with self.table_placeholder.container():
            Table(df,"Anomaly data")
