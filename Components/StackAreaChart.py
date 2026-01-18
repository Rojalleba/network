import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

class StackAreaChart:
    def __init__(self):
        pass

    def render(self,df):
        df_long = df.melt(
            id_vars="window_start",
            value_vars=["bytes_forward", "bytes_backward"],
            var_name="direction",
            value_name="bytes"
        )

        # Create stacked area chart
        fig = px.area(
            df_long,
            x="window_start",
            y="bytes",
            color="direction",
            title="Bytes Forward vs Backward (Stacked Area)"
        )
        st.plotly_chart(fig)
        
        