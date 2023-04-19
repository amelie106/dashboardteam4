import streamlit as st
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

import pandas as pd
import altair as alt

@st.cache_data()
def load_data():
    df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text("Done! Enjoy the dashboard!")

# Define a function to plot the COVID-19 cases for selected countries
@st.cache_data
def plot_covid_cases(start_date, end_date, selected_countries, granularity, data, column_name, plot_type, location_col, peak_detection = False):
    x_col = 'date'
    y_col = column_name

    # Convert start_date and end_date to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the data for the selected time period and countries
    filtered_df = data[(data['date'] >= start_date) & (data['date'] <= end_date) &
                       (data['location'].isin(selected_countries))]

    # Set the granularity of the data
    if granularity == 'Month':
        filtered_df = filtered_df.groupby([pd.Grouper(key='date', freq='M'), 'location']).sum().reset_index()
    elif granularity == 'Week':
        filtered_df = filtered_df.groupby([pd.Grouper(key='date', freq='W'), 'location']).sum().reset_index()
    else:
        filtered_df = filtered_df.groupby(['date', 'location']).sum().reset_index()

    # Create a selector for countries and continents
    # added missing location_col parameter and options initialization
    if location_col == 'Continent':
        filtered_df = filtered_df.groupby(['continent']).sum().reset_index()
        options = filtered_df['continent'].unique()
    elif location_col == 'Country':
        options = filtered_df['location'].unique()

    # Plot the COVID-19 cases for each country or continent
    if plot_type == 'Total Cases':
        y_col = 'total_cases'
        y_label = 'Total COVID-19 Cases'
    elif plot_type == 'New Cases per Million Inhabitants':
        y_col = 'new_cases_per_million'
        y_label = 'New Cases per Million Inhabitants'
    elif plot_type == "New Cases":
        y_col = 'new_cases'
        y_label = 'Total COVID-19 New Cases'
    elif plot_type == 'Total Deaths':
        y_col = 'total_deaths'
        y_label = 'Total COVID-19 Deaths'
    elif plot_type == 'New Deaths':
        y_col = 'new_deaths'
        y_label = 'New Deaths'
    elif plot_type == 'Rolling average':
        y_col = 'new_cases'
        y_label = 'Rolling Average of New Cases'
        filtered_df = filtered_df.groupby('location').rolling(7, min_periods=1).mean().reset_index()
    else:
        raise ValueError('Invalid plot type')

    # Peak detection
    if peak_detection:
        filtered_df['derivative'] = filtered_df[column_name].diff()
        derivative = alt.Chart(filtered_df).mark_line().encode(
            x=x_col,
            y='derivative'
        )
    else:
        derivative = alt.Chart(filtered_df).mark_line().encode().properties()

    # Determine the level of granularity based on user input
    if granularity == 'Month':
        x_col = pd.Grouper(key='date', freq='M')
    elif granularity == 'Week':
        x_col = pd.Grouper(key='date', freq='W')
    else:
        x_col = 'date'

    chart = alt.Chart(filtered_df).mark_line().encode(
        x='date:T',
        y=y_col,
        color='location'
    ).properties(
        width=800,
        height=500,
        title=f"{column_name} by country"
    ).interactive()

    # Add text labels for the countries and their respective continents
    labels = alt.Chart(filtered_df.groupby('location', as_index=False).tail(1)).mark_text(align='left', dx=5).encode(
        x='date:T',
        y=y_col,
        text=alt.Text('location'),
        color=alt.Color('location', legend=None),
        tooltip=['location', alt.Tooltip(y_col, format=',')]
    )

    chart = (derivative + chart + labels).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        gridOpacity=0.4
    )

    chart = chart.configure_legend(
        title=None,
        labelFontSize=12,
        labelLimit=100,
        symbolSize=200)

    # Display the chart
    st.altair_chart(chart, use_container_width=True)

    return chart

def get_selected_countries():
    selected_countries = [...] # retrieve the selected countries from user input
    return selected_countries
selected_countries = get_selected_countries()

# Define the Streamlit app
def app():

    #Sidebars
    #Title
    st.sidebar.header("Dashboard `Covid-19`")

    # Define the time period to display
    st.sidebar.subheader("Timeline")

    if 'start_date' not in locals():
        start_date = pd.to_datetime('2020-01-01')
    if 'end_date' not in locals():
        end_date = pd.to_datetime('2020-01-31')

    timespan = st.sidebar.date_input("Pick the timeframe", (start_date, end_date))

    if (len(timespan) == 2):
        start_date = timespan[0]
        end_date = timespan[1]

    # Add a dropdown menu for the user to select the view of new_cases, total_death and new_deaths
    st.sidebar.subheader("Parameters")
    plot_type = st.sidebar.selectbox('Select view type', ['Cases', 'Deaths'])
    location_col = st.sidebar.selectbox('Select location', ['Continent', 'Country'])

    # Define the possible columns to display for each view type
    columns_dict = {
        'Cases': ['total_cases', 'new_cases', 'total_cases_per_million', 'new_cases_per_million'],
        'Deaths': ['total_deaths', 'new_deaths', 'total_deaths_per_million', 'new_deaths_per_million']
    }

    # Define the column to use for the selected view type
    column_name = st.sidebar.selectbox(f'Select column for {plot_type}', columns_dict[plot_type])

    # Activate checkbox for peak detection only for cumulative values
    if 'total' in column_name:
        peak_detection = st.sidebar.checkbox(f'Activate peak detection', value=False)
    else:
        peak_detection = False

    # Add a selector for the user to choose between Continent and Country
    # Create a selector for countries and continents
    if location_col == 'Continent':
        filtered_df = data.groupby(['continent']).sum().reset_index()
        location_col = 'continent'
        options = filtered_df['continent'].unique()
    elif location_col == 'Country':
        location_col = 'location'
        options = data['location'].unique()

    # Add a selector for the user to choose which countries/continents to plot
    selected_location = st.multiselect(f"Select {location_col}s", options=options)
    # Add a dropdown menu for plot type selection
    plot_type = st.selectbox('Select plot type', ['Total Cases', 'New Cases per Million Inhabitants'])

    # Add a dropdown menu for granularity selection
    st.sidebar.subheader("Granularity")
    granularity = st.sidebar.selectbox('Select the level of granularity', ['Week', 'Month'])

    # Call the function to plot the COVID-19 cases for the selected time period and countries
    if selected_countries:
        st.write(f'COVID-19 Cases for {", ".join(selected_countries)}')
        plot_covid_cases(start_date, end_date, selected_countries, granularity, data, column_name, plot_type, location_col, peak_detection = False)

    st.sidebar.markdown('''
    ---
    By Amelie,  Andreea and Clem
    ''')
app()
