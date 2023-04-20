import streamlit as st
import pandas as pd
import altair as alt


st.set_page_config(layout="wide", initial_sidebar_state="expanded")


@st.cache_data()
def load_data():
    df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text("Done! Enjoy the dashboard!")

# Create a dictionary that maps countries to their respective continents
continents = {'North America': ['Canada', 'United States', 'Mexico'],
              'South America': ['Brazil', 'Argentina', 'Colombia'],
              'Europe': ['United Kingdom', 'France', 'Germany', 'Italy', 'Spain'],
              'Asia': ['China', 'India', 'Japan', 'South Korea'],
              'Africa': ['South Africa', 'Nigeria', 'Egypt'],
              'Oceania': ['Australia', 'New Zealand']}


# Define a function to plot the COVID-19 cases for selected countries
@st.cache_data
def plot_covid_cases(start_date, end_date, selected_countries, granularity, data, column_name, peak_detection = False):
    x_col = 'date'
    y_col = column_name

    # Convert start_date and end_date to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the data for the selected time period and countries
    filtered_df = data[(data['date'] >= start_date) & (data['date'] <= end_date) &
                       (data['location'].isin(selected_countries))]

    # Set the granularity of the data depending on whether it is cumulative or not
    if 'total' in column_name:
        if granularity == 'Month':
            filtered_df = filtered_df.groupby([pd.Grouper(key='date', freq='M'), 'location']).tail(1).reset_index()
        elif granularity == 'Week':
            filtered_df = filtered_df.groupby([pd.Grouper(key='date', freq='W'), 'location']).tail(1).reset_index()
        else:
            filtered_df = filtered_df.groupby(['date', 'location']).tail(1).reset_index()
    else:
        if granularity == 'Month':
            filtered_df = filtered_df.groupby([pd.Grouper(key='date', freq='M'), 'location']).sum().reset_index()
        elif granularity == 'Week':
            filtered_df = filtered_df.groupby([pd.Grouper(key='date', freq='W'), 'location']).sum().reset_index()
        else:
            filtered_df = filtered_df.groupby(['date', 'location']).sum().reset_index()

    # Categorize the countries by continents
    def get_continent(country):
        for continent, countries in continents.items():
            if country in countries:
                return continent
        return "Other"

    country_groups = filtered_df.groupby('location')['location'].first().apply(get_continent).to_dict()

    # Peak detection
    if peak_detection:
        filtered_df['derivative'] = filtered_df[column_name].diff()
        derivative = alt.Chart(filtered_df).mark_line().encode(
            x=x_col,
            y='derivative'
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
    plot_type = st.sidebar.selectbox('Select view type', ['Cases', 'Deaths'])

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

    # Define the countries or continents to display
    st.sidebar.subheader("Country")
    selected_countries = st.sidebar.multiselect('Select countries or continent to display', data['location'].unique())

    # Add a dropdown menu for granularity selection
    st.sidebar.subheader("Granularity")
    granularity = st.sidebar.selectbox('Select the level of granularity', ['Day', 'Week', 'Month'])

    # Call the function to plot the COVID-19 cases for the selected time period and countries
    if selected_countries:
        st.write(f'COVID-19 Cases for {", ".join(selected_countries)}')
        plot_covid_cases(start_date, end_date, selected_countries, granularity, data, column_name, peak_detection)

    st.sidebar.markdown('''
    ---
    By Amelie, Andreea and Clem
    ''')
app()
