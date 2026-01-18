import pandas as pd
import plotly.express as px
import streamlit as st

class LineChart:
    def __init__(self,title="Line Chart"):     
        self.title = title
        fig = None


    def render(self,df,x_col, y_col):
        
        fig = px.line(df, x=x_col, y=y_col, title=self.title,width=150,height=500)
        st.plotly_chart(fig)