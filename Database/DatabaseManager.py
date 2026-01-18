import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
from psycopg2.extras import execute_batch


class DatabaseManager:
    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur = self.conn.cursor()
        self._create_table()
        
        # ['Protocol', 'source', 'destination', 'sport', 'dport', 'avg_size', 'pkt_size_var', 'packet_count', 'PacketsSent', 'PacketsReceived', 'BytesSent', 'BytesReceived', 'avg_ttl', 'syn_count', 'fin_count', 'ack_count', 'first_ts', 'last_ts', 'interarrival_var', 'syn_ack_ratio', 'Duration', 'direction_ratio', 'contact_frequency', 'is_known_service']
        
    def _create_table(self):
        """Create the table for new traffic live data"""
        create_table_query = """
            CREATE TABLE IF NOT EXISTS hostBasedSystem (
                id SERIAL PRIMARY KEY,
                packet_count INT,
                interarrival_var DOUBLE PRECISION,
                packet_size_variance DOUBLE PRECISION,
                syn_ack_ratio DOUBLE PRECISION,
                connection_duration DOUBLE PRECISION,
                bytes_forward BIGINT,
                bytes_backward BIGINT,
                is_cloud_service INT,
                
                cpu_avg DOUBLE PRECISION,
                mem_avg DOUBLE PRECISION,
                active_connections_avg DOUBLE PRECISION,
                open_ports_count INT,
                window_start TIMESTAMP,
                window_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        self.cur.execute(create_table_query)
        self.conn.commit()

    def insert_new_traffic(self, df):
        """Insert rows into hostBasedSystem table"""
        
        query = """
            INSERT INTO hostBasedSystem (
                packet_count,
                interarrival_var,
                packet_size_variance,
                syn_ack_ratio,
                connection_duration,
                bytes_forward,
                bytes_backward,
                is_cloud_service,
                cpu_avg,
                mem_avg,
                active_connections_avg,
                open_ports_count,
                window_start,
                window_end
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s)
        """

        data = []

        # Case 1: if df is a dictionary
        if isinstance(df, dict):
            data.append((
                df.get("packet_count"),
                float(df.get("interarrival_var")),
                float(df.get("packet_size_variance")),
                float(df.get("syn_ack_ratio")),
                float(df.get("connection_duration")),
                df.get("bytes_forward"),
                df.get("bytes_backward"),
                df.get("is_cloud_service"),
                float(df.get("cpu_avg")),
                float(df.get("mem_avg")),
                float(df.get("active_connections_avg")),
                df.get("open_ports_count"),
                df.get("window_start"),
                df.get("window_end")
            ))

        # Case 2: if df is a pandas DataFrame
        else:
            for row in df.itertuples(index=False):
                data.append(tuple(row))

        execute_batch(self.cur, query, data)
        self.conn.commit()
        print(f"{len(data)} rows inserted successfully!")



    def insert_user(self,username,password):
        query = f"""
            INSERT INTO users
            (username,password)
            values({username},{password})
        """
        self.cur.execute(query)
        self.conn.commit()
    
    def validate_user(self, username, password):
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        self.cur.execute(query, (username, password))
        result = self.cur.fetchone()  # fetch one matching record
        return result is not None

        
    def fetch_all(self):
        """Fetch all packets as a DataFrame"""
        df = pd.read_sql(f"SELECT * FROM hostBasedSystem ORDER BY id ASC", self.conn)
        return df
    
    def get_last_ten(self):
        try:
            query = f"""
                SELECT *
                FROM hostBasedSystem
                ORDER BY window_start DESC
                LIMIT 10;
            """
            with self.conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]

            df = pd.DataFrame(rows, columns=colnames)
            return df
        except Exception as e:
            print("Exception from Database ",e)
      
        
    def convert_to_csv(self):
        query = f"""select * from hostBasedSystem"""
        df = pd.read_sql_query(query, self.conn)
        df.to_csv("D:/network/models/traffic_live.csv", index=False)
        print("Data exported to CSV successfully")
        
    def close(self):
        """Close connection"""
        self.cur.close()
        self.conn.close()
