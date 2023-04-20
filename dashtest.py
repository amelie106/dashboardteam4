import streamlit as st
import pandas as pd
import altair as alt


@st.cache_data()
def load_data():
    df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
    df = df.rename(columns= {'date': 'Date',
                             'new_cases': 'New cases', 'new_cases_per_million' : 'New cases per million', 
                             'total_cases':'Total cases', 'total_cases_per_million' : 'Total cases per million',
                             'new_deaths' : 'New deaths', 'new_deaths_per_million': 'New deaths per million',
                             'total_deaths' : 'Total deaths', 'total_deaths_per_million': 'Total deaths per million'})
    df['Date'] = pd.to_datetime(df['Date'])
    return df


# Setup
st.set_page_config(page_title = "Covid-19 Dashboard", page_icon = ":warning:",  layout="wide", initial_sidebar_state="expanded")
st.title(":face_with_thermometer: Pandemic Evolution over time")
CONTINENTS = ['Africa', 'North America', 'South America', 'Europe', 'Oceania', 'Asia']
data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text("Done! Enjoy the dashboard!")

# Define a function to plot the COVID-19 cases for selected countries
@st.cache_data
def plot_covid_cases(start_date, end_date, selected_locations, granularity, data, column_name, peak_detection):
    x_col = 'Date'
    y_col = column_name

    # Convert start_date and end_date to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the data for the selected time period and countries
    filtered_df = data[(data['Date'] >= start_date) & (data['Date'] <= end_date) &
                       (data['location'].isin(selected_locations))]

    # Set the granularity of the data depending on whether it is cumulative or not
    if 'Total' in column_name:
        if granularity == 'Month':
            filtered_df = filtered_df.groupby([pd.Grouper(key='Date', freq='M'), 'location']).tail(1).reset_index()
        elif granularity == 'Week':
            filtered_df = filtered_df.groupby([pd.Grouper(key='Date', freq='W'), 'location']).tail(1).reset_index()
        else:
            filtered_df = filtered_df.groupby(['Date', 'location']).tail(1).reset_index()
    else:
        if granularity == 'Month':
            filtered_df = filtered_df.groupby([pd.Grouper(key='Date', freq='M'), 'location']).sum().reset_index()
        elif granularity == 'Week':
            filtered_df = filtered_df.groupby([pd.Grouper(key='Date', freq='W'), 'location']).sum().reset_index()
        else:
            filtered_df = filtered_df.groupby(['Date', 'location']).sum().reset_index()

    # Peak detection
    if peak_detection:
        filtered_df['derivative'] = filtered_df[column_name].diff()
        filtered_df['derivative'] = filtered_df['derivative'].apply(lambda x: x if x > 0 else 0)
        derivative = alt.Chart(filtered_df).mark_line().encode(
            x=x_col,
            y='derivative',
            #color='location',
            strokeDash=alt.value([5, 5]),
            color = alt.Color('Value:Q', scale=alt.Scale(scheme='reds')),
            tooltip = ['Country:N', 'Value:Q']
        )
    else:
        derivative = alt.Chart(filtered_df).mark_line().encode().properties()

    # Create chart
    chart = alt.Chart(filtered_df).mark_line().encode(
        x=x_col,
        y=y_col,
        color='location'
    ).properties(
        width=800,
        height=500,
        title=f"{column_name} by country"
    ).interactive()

    # Add text labels for the countries and their respective continents
    labels = alt.Chart(filtered_df.groupby('location', as_index=False).tail(1)).mark_text(align='left', dx=5).encode(
        x=x_col,
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
    location_col = st.sidebar.selectbox('Select location type', ['Continent', 'Country'])

    # Add a selector for the user to choose between Continent and Country
    # Create a selector for countries and continents
    if location_col == 'Continent':
        options = CONTINENTS
    elif location_col == 'Country':
        options = [item for item in data['location'].unique() if item not in CONTINENTS]
        
    selected_locations = st.sidebar.multiselect(f"Select {location_col.lower()}s", options=options)

    # Define the possible columns to display for each view type
    plot_type = st.sidebar.selectbox('Select view type', ['Cases', 'Deaths'])

    columns_dict = {
        'Cases': ['New cases', 'Total cases', 'New cases per million', 'Total cases per million'],
        'Deaths': ['New deaths', 'Total deaths', 'New deaths per million', 'Total deaths per million']
    }

    # Define the column to use for the selected view type
    column_name = st.sidebar.selectbox(f'Select column for {plot_type}', columns_dict[plot_type])

    # Activate checkbox for peak detection only for cumulative values
    if 'Total' in column_name:
        peak_detection = st.sidebar.checkbox(f'Activate peak detection', value=False)
    else:
        peak_detection = False

    # Add a dropdown menu for granularity selection
    st.sidebar.subheader("Granularity")
    granularity = st.sidebar.selectbox('Select the level of granularity', ['Day', 'Week', 'Month'])

    # Call the function to plot the COVID-19 cases for the selected time period and countries
    if selected_locations:
        st.write(f'COVID-19 Cases for {", ".join(selected_locations)}')
        plot_covid_cases(start_date, end_date, selected_locations, granularity, data, column_name, peak_detection)

    st.sidebar.markdown('''
    ---
    By Amelie, Andreea and Clem
    ''')
app()
