import plotly.express as px
import streamlit as st

class ScatterPlot:
    counter = 0
    def __init__(self,df,x_axis,y_axis,color,hover):
        fig = px.scatter(
            df,
            x = f"{x_axis}",
            y = f"{y_axis}",
            color = f"{color}",
            hover_data = f"{hover}",
            title = f'Scatter Plot of {x_axis } vs {y_axis}'
        )
        ScatterPlot.counter += 1
        st.plotly_chart(fig,key=f"scatter_{ScatterPlot.counter}")