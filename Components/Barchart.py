import plotly.express as px
import streamlit as st

class Barchart:
    counter = 0
    def __init__(self,df,x_axis,y_axis,title):
        fig = px.bar(df,
               x=f"{x_axis}",
               y=f"{y_axis}",
               barmode="group",
               title=f"{title}"
               )
        fig.update_yaxes(range=[0, 100000],
                         title=f"{y_axis}"
                         )
        Barchart.counter+=1
        st.plotly_chart(fig,key=f"Barchart{Barchart.counter}")