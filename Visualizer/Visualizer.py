import streamlit as st
import pandas as pd

class DataTableVisualizer:
    def __init__(self, data: pd.DataFrame, title: str = "Data Table"):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        self.data = data
        self.title = title


