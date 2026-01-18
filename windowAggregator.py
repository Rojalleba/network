import time
import pandas as pd
from datetime import datetime
from collections import defaultdict

WINDOW_SIZE = 5  # seconds

class WindowAggregator:
    def __init__(self):
        self.window_packets = []
        self.window_start_time = datetime.now()

    def add_packet(self, packet):
        """Append new packet msg dictionary here."""
        self.window_packets.append(packet)

    def window_ready(self):
        return (datetime.now()-self.window_start_time).total_seconds() >= WINDOW_SIZE

    def reset_window(self):
        self.window_packets = []
        self.window_start_time = datetime.now()
