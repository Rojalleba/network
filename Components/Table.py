import streamlit as st

class Table:
    def __init__(self,df,title):
        try:
            st.subheader(f"{title}")
            st.dataframe(df)
        except Exception as e:
            print("Error coming from Table component",e)
