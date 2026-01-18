import numpy as np
import pandas as pd
from collections import defaultdict
import psutil

def compute_features(packets):
    if len(packets) == 0:
        return None

    df = pd.DataFrame(packets)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    

    # -------------------------
    # 1) Inter-arrival variance
    # -------------------------
    df = df.sort_values("timestamp")
    df['inter_arrival'] = df['timestamp'].diff().dt.total_seconds().fillna(0)
    inter_arrival_var = df['inter_arrival'].var()

    # -----------------------------------------
    # 2) Packet size variance over time (bytes)
    # -----------------------------------------
    size_variance = df['size'].var()

    # -------------------
    # 3) SYN/ACK ratio
    # -------------------
    syn_count = df['syn_flag'].sum()
    ack_count = df['ack_flag'].sum()
    syn_ack_ratio = syn_count / ack_count if ack_count > 0 else syn_count

    # -------------------------
    # 4) Connection duration
    # -------------------------
    connection_duration = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).total_seconds()

    # -----------------------------------------------------------
    # 5) Bytes per flow direction (src → dst and dst → src)
    # -----------------------------------------------------------
    flows = defaultdict(lambda: {"forward": 0, "backward": 0})

    for _, row in df.iterrows():
        key = tuple(sorted([row['source'], row['destination']]))  # normalized flow pair

        if row['source'] < row['destination']:
            flows[key]["forward"] += row['size']
        else:
            flows[key]["backward"] += row['size']

    total_forward_bytes = sum(v["forward"] for v in flows.values())
    total_backward_bytes = sum(v["backward"] for v in flows.values())

    # -------------------------
    # 6) Known service tag
    # -------------------------
    # Example heuristic: destination is cloud IP range
    def is_cloud_ip(ip):
        return ip.startswith("3.") or ip.startswith("13.") or ip.startswith("18.") or ip.startswith("52.")

    is_cloud = 1 if any(is_cloud_ip(ip) for ip in df["destination"]) else 0

    
    # -------------------------
    # Host-level features aggregated
    # -------------------------
    
    cpu_avg = df['cpu_percent'].mean() if 'cpu_percent' in df.columns else 0
    mem_avg = df['mem_percent'].mean() if 'mem_percent' in df.columns else 0
    active_connections_avg = df['active_connections'].mean() if 'active_connections' in df.columns else 0
    open_ports_count = len([c for c in psutil.net_connections(kind='inet') if c.status == 'LISTEN'])    
    
    
    
    
    # return aggregated window
    return {
        "packet_count": len(df),
        "interarrival_var": inter_arrival_var,
        "packet_size_variance": size_variance,
        "syn_ack_ratio": syn_ack_ratio,
        "connection_duration": connection_duration,
        "bytes_forward": total_forward_bytes,
        "bytes_backward": total_backward_bytes,
        "is_cloud_service": is_cloud,
        "cpu_avg":cpu_avg,
        "mem_avg":mem_avg,
        "active_connections_avg":active_connections_avg,
        "open_ports_count": open_ports_count,
        "window_start": df["timestamp"].iloc[0],
        "window_end": df["timestamp"].iloc[-1]
    }
