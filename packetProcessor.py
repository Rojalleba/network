import pandas as pd
import numpy as np
from scapy.all import *
from datetime import datetime
import threading
from kafka import KafkaProducer, KafkaConsumer
import json
from Database.DatabaseManager import DatabaseManager
import streamlit as st
# from DashboardVisualizer import DashboardVisualizer
import time
import psutil

class PacketProcessor:
    def __init__(self, window_size=5, kafka_server='localhost:9092'):
        # Database
        self.db = DatabaseManager(dbname='network_anomaly', user='postgres', password='postgres')

        # Threads control
        self.sniffing = False
        self.lock = threading.Lock()
        self.window_size = window_size
        self.thread_agg = None
        self.thread = None
        self.packet_toggle = False
        self.port_process_map = {}
        self.last_map_update = 0
        
        # Kafka
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_server,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.kafka_server = kafka_server

        # # Data buffers
        self.agg_packets = []
        self.groupby_source_packets = []
        self.featured_data = []
        
        import socket
        self.my_host_ip = socket.gethostbyname(socket.gethostname())
        # Session state
    
        if 'stop_event' not in st.session_state:
            st.session_state.stop_event = threading.Event()
        

    # ----------------- Packet Sniffing / Producer -----------------
    def get_host_stats(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),  # non-blocking
            "mem_percent": psutil.virtual_memory().percent,
            "active_connections": len(psutil.net_connections(kind='inet'))
        }
        
    def build_port_process_map(self):
        """Build local port -> process name mapping"""
        port_process = {}
        for conn in psutil.net_connections():
            if conn.laddr:
                try:
                    port_process[conn.laddr.port] = psutil.Process(conn.pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        self.port_process_map = port_process
    
    def get_process_name(self, src_port):
        """Return process name from cached map"""
        return self.port_process_map.get(src_port)

    
    def process_packet(self, packet):
        try:
            if IP in packet:
                size = len(packet)
                proto = packet[IP].proto
                    
                # Get ports if TCP/UDP
                if TCP in packet:
                    src_port = packet[TCP].sport
                    dst_port = packet[TCP].dport
                elif UDP in packet:
                    src_port = packet[UDP].sport
                    dst_port = packet[UDP].dport
                else:
                    src_port = dst_port = None
                
                self.build_port_process_map()
                # Map src_port to process name
                process_name = self.get_process_name(src_port)
                
                data = {
                    'timestamp': str(datetime.now()),
                    'source': packet[IP].src,
                    'destination': packet[IP].dst,
                    'Protocol': proto,
                    'src_port': src_port,
                    'dst_port': dst_port,
                    'process': process_name,
                    'size': size,
                    'ttl': packet[IP].ttl,
                    'syn_flag': int(TCP in packet and packet[TCP].flags & 0x02 != 0),
                    'fin_flag': int(TCP in packet and packet[TCP].flags & 0x01 != 0),
                    'ack_flag': int(TCP in packet and packet[TCP].flags & 0x10 != 0)
                }

                # Send packet to Kafka asynchronously
                # print("Packets \n",data)
            
                data.update(self.get_host_stats())
                self.producer.send('packets-topic', value=data)
                
        except Exception as e:
            print(f"[PacketProcessor] Error processing packet: {e}")
            
#-----------------Aggregate if needed------------ 
    def _aggregate_if_needed(self):
        try:
            now = datetime.now()
            elapsed = (now - self.last_window_time).total_seconds()
            if elapsed < self.window_size:
                return
            if self.agg_packets:
                    df = pd.concat(self.agg_packets, ignore_index=True)
                    self.groupByProtocol(df)
                    self.groupBySource(df)
                    self.featured_data.append(df) 
                    self.agg_packets.clear()
                    self.groupby_source_packets.clear()
                    self.last_window_time = now                   
        except Exception as e:
            print("Something wrong at Aggregate method ",e)
            
            
 # ----------------- groupby -----------------
    def groupByProtocol(self, df):
        try:
            protocol = df.groupby('Protocol').agg(
                avg_size=('size', 'mean'),
                packet_count=('size', 'count'),
                avg_ttl=('ttl', 'mean'),
                syn_count=('syn_flag', 'sum'),
                fin_count=('fin_flag', 'sum'),
                ack_count=('ack_flag', 'sum')
            ).reset_index()
            self.agg_packets.append(protocol)
            self.producer.send('packets-groupByProtocol', value = protocol)
        except Exception as e:
            print("Something wrong during grouping by protocol ",e)


    def groupBySource(self, df):
        try:
            groupbysource = df.groupby('source').agg(
                avg_size=('size', 'mean'),
                BytesSent=('size', 'sum'),
                PacketsSent=('size', 'count'),
                avg_ttl=('ttl', 'mean'),
                syn_count=('syn_flag', 'sum'),
                fin_count=('fin_flag', 'sum'),
                ack_count=('ack_flag', 'sum')
            ).reset_index()
            self.groupby_source_packets.append(groupbysource)
            self.producer.send('packets-groupBySource', value = groupbysource)
        except Exception as e:
            print("Something wrong at grouped by source ",e)
  
        
    def start_sniffing(self):
        print("start_sniff",self)
        if not self.sniffing:
            self.sniffing = True
            st.session_state.start_sniffing = True
            if self.thread is None:
                self.thread = threading.Thread(target=self._capture_packets, daemon=True)
                self.thread.start()
                print("Self ",self.thread.is_alive)
                
                # self.thread_agg = threading.Thread(target=self._aggregate_if_needed,daemon=True)
                # self.thread_agg.start()
                
            # Start packet capture thread
                print("[PacketProcessor] Sniffing started")

    def stop_sniffing(self):
        print("stop_sniff",self)
        self.sniffing = False
        st.session_state.start_sniffing = False
        if self.thread is not None:
            st.session_state.stop_event.set()
            self.thread.join()
            self.thread = None
            # self.thread_agg.join()
            print("[PacketProcessor] Sniffing stopped")


    def _capture_packets(self):
        sniff(prn=self.process_packet, store=False, stop_filter=lambda p: not self.sniffing)

    # ----------------- Kafka Consumer -----------------
    def _consume_packets(self):
        consumer = KafkaConsumer(
            'packets-topic',
            bootstrap_servers=self.kafka_server,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='packet-processor'
        )

        for msg in consumer:
            if not self.sniffing:
                break

            packet_data = msg.value
            with self.lock:
                # Convert timestamp back to datetime
                packet_data['timestamp'] = pd.to_datetime(packet_data['timestamp'])

                # Append to aggregation buffers
                self._append_packet(packet_data)

    def _append_packet(self, packet_data):
        df = pd.DataFrame([packet_data])
        self.groupByProtocol(df)
        self.groupBySource(df)
        self._aggregate_if_needed()

    # ----------------- Dashboard -----------------
    def _run_dashboard(self):
        while self.sniffing:
            with self.lock:
                raw_df = pd.concat(self.agg_packets, ignore_index=True) if self.agg_packets else pd.DataFrame()
                source_df = pd.concat(self.groupby_source_packets, ignore_index=True) if self.groupby_source_packets else pd.DataFrame()

            if not raw_df.empty or not source_df.empty:
                self.dv.update_data(rawFrame=raw_df, groupBySource=source_df)
                self.dv.run_live_dashboard()

            time.sleep(2)

    # ----------------- Anomaly Detection -----------------
    def _run_anomaly_detection(self):
        last_index = 0
        while self.sniffing:
            with self.lock:
                if not self.featured_data:
                    time.sleep(1)
                    continue
                df = pd.concat(self.featured_data, ignore_index=True)

            new_df = df.iloc[last_index:]
            if not new_df.empty:
                # Your ML pipeline here
                st.session_state.pipeline.Predict_Anomaly(new_df)
                self.db.insert_packet(new_df)
                last_index = len(df)

            time.sleep(5)
