import pandas as pd
import streamlit as st

df = pd.read_csv('cereal.csv')

# dashboard title
st.title("Real-Time / Live Data Science Dashboard")

# top-level filters
job_filter = st.selectbox("Select the Cereal", pd.unique(df["name"]))

# creating a single-element container
placeholder = st.empty()

# dataframe filter
df = df[df["name"] == job_filter]
df = df.melt(id_vars='name')
print(df)
st.bar_chart(df, x='variable', y='value')