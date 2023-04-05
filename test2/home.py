import matplotlib as matplotlib
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from matplotlib.backends._backend_agg import RendererAgg

st.set_page_config(layout="wide")
st.title("The 500 richest persons in the world")
st.header("Who are they?")

df = pd.read_csv("rich.csv", sep=";")
del df["Unnamed: 7"],df["Unnamed: 8"], df['Unnamed: 9'], df['Unnamed: 10']

#Creating categories
st.sidebar.header('Select what to display')

#multiselect
industries = df['Industry'].unique().tolist()
industry_selected = st.sidebar.multiselect('Type of industry', industries, industries)

#slicer
rank_rich = df["Rank"]
slicer_nb_rich = st.sidebar.slider("Ranking of the person", int(rank_rich.min()), int(rank_rich.max()), (int(rank_rich.min()), int(rank_rich.max())), 1)

st.header("Industries with the richest persons")
# fig, ax = plt.subplots(figsize=(5, 5))
# ax.pie(industries, wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white'}

count_by_industry = df.Industry.value_counts()
st.write(count_by_industry)
st.bar_chart(count_by_industry)


