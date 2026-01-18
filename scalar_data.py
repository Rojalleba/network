import pandas as pd
import numpy as np

numeric_features = [
    'et_count', 'interarrival_var', 'packet_size_variance', 'syn_ack_ratio',
    'connection_duration', 'bytes_forward', 'bytes_backward',
    'cpu_avg', 'mem_avg', 'active_connections_avg', 'open_ports_count'
]
categorical_features = ['is_cloud_service']

# Convert message to DataFrame
df_msg = pd.DataFrame([message])

# Scale numeric features
X_scaled = scaler.transform(df_msg[numeric_features])

# Combine with categorical
X = np.hstack([X_scaled, df_msg[categorical_features].values])
