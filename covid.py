import pandas as pd
import streamlit as st

df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', 
                 usecols = ['continent', 'location', 'new_cases_per_million', 'date'])

# Select and filter by Continent
df = df[df['continent'].notna()]
continent_filter = st.selectbox("Select the Continent", pd.unique(df["continent"]))
df = df[df["continent"] == continent_filter]
df = df.drop(columns='continent')

# Create Matrix with location x date
df = df.pivot(index='date', columns='location')
df.columns = [item[1] for item in list(df.columns.to_flat_index())]

# Create dashboard
st.title("New Covid-19 cases per million per country")
st.line_chart(df)