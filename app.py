### Visualizing Motor Vehicle Accidents in NYC using a Streamlit Web App ###

# Import required python library
import streamlit as st         # Streamlit for deploying webapp 
import numpy as np             
import pandas as pd
import pydeck as pdk           # PyDeck for for creating beautiful maps
import plotly.express as px    # Plotly Express for interactive chart plotting


# Url of the dataset we are using, you can get the dataset from https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95
DATA_URL = (
    "Motor_Vehicle_Collisions_-_Crashes.csv"
)


# Insert title and some text on the webpage
st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a streamlit dashboard that can be used "
"to analyse motor vehicles collisions in NYC")


# Load data for visualization purposes
@st.cache(persist = True) # This line restrict streamlit to run this function if not necessary, since it takes some time to load
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows = nrows, parse_dates = [['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset = ['LATITUDE', 'LONGITUDE'], inplace = True)
    data.rename(lambda x : str(x).lower(), axis = 'columns', inplace = True)
    data.rename(columns = {'crash_date_crash_time' : 'date/time'}, inplace = True)
    return data
data = load_data(100000)
original_data = data


# First Exploratory question, insert a slider to ask for min number of people injured and display the result on a map
st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[['latitude', 'longitude']].dropna(how = 'any'))


# Second Exploratory question, using slider to ask for which hour of the day to look at and then using pydeck to plot a 3D map
st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]
st.markdown("Vehicle collision between {}:00 to {}:00".format(hour, (hour+1)%24))
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude" : np.average(data['latitude']),
        "longitude" : np.average(data['longitude']),
        "zoom" : 11,
        "pitch" : 50,
    },
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data = data[['date/time', 'latitude', 'longitude']],
            get_position = ['longitude', 'latitude'],
            radius = 100,
            extruded = True,
            pickable = True,
            elevation_scale = 4,
            elevation_range = [0,1000],
        ),
    ],
))


# Third Exploratory question ,providing breakdown by minute by plotting an interactive histogram  using plotly express
st.subheader("Breakdown by minute between {}:00 and {}:00".format(hour, (hour+1)%24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
fig = px.bar(chart_data, x = 'minute', y = 'crashes', hover_data = ['minute', 'crashes'], height = 400)
st.write(fig)


# Fourth Exploratory question, using a dropdown to select type of affected people and returning top 5 dangeroud streets for the affected type
st.header("Top5 most dangerous streets by affected people")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])
if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[['on_street_name', 'injured_pedestrians']].sort_values(by = ['injured_pedestrians'], ascending = False).dropna(how = 'any')[:5])
elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[['on_street_name', 'injured_cyclists']].sort_values(by = ['injured_cyclists'], ascending = False).dropna(how = 'any')[:5])
elif select == 'Motorists':
    st.write(original_data.query("injured_motorists >= 1")[['on_street_name', 'injured_motorists']].sort_values(by = ['injured_motorists'], ascending = False).dropna(how = 'any')[:5])


# Providing a checkbox for those who want to explore the raw data
if st.checkbox("Show Raw Data", False) :
    st.subheader("Raw Data")
    st.write(original_data)