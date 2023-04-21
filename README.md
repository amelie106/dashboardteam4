# COVID-19 Dashboard

## Project Description

This is a university data analysis project on COVID-19 data, specifically cases/deaths per country as a function of time. 
The visualization of the evolution of the pandemic is accessible as an interactive dashboard.
As it is a commonly used and reliable source, we referred to the data from [Our World in Data](https://ourworldindata.org/covid-cases).

## Collaborators

- [Clem](https://github.com/CryptoClemzilla)
- [Andreea](https://github.com/andreeastroia)
- [Amelie](https://github.com/amelie106)

## Instructions

To run this project, you will need to have Python (version 3.8 or higher) preinstalled. If you are using MacOS or Linux, this should already be the case. If you are on Windows, please refer to [this page](https://www.tomshardware.com/how-to/install-python-on-windows-10-and-11) for instructions.


### 1. Create environment
Open a terminal in the root directory and create an environment like this:

```
python -m venv env
```


### 2. Activate environment
If you are using MacOS or Linux, run the following command to activate your environment:

```
source env/bin/activate
```

If you are using Windows, run this instead:

```
env\Scripts\activate
```


### 3. Install dependencies
Finally, install the requirements for this project by running the following command:

```
python -m pip install -r requirements.txt
```


## Running the dashboard

To execute the dashboard locally, run the following command:

```
streamlit run dashboard.py
```


## Accessing the dashboard


To access the dashboard on the Cloud, please follow the following link [here](https://dashing-ladies-covid-data.streamlit.app/)
