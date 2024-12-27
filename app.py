import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

# dataset URL
DATA_URL = "https://raw.githubusercontent.com/carlosfab/curso_data_science_na_pratica/master/modulo_02/ocorrencias_aviacao.csv"

# Major cities in Indonesia (latitude, longitude) including Kalimantan
INDONESIA_CITIES = {
    "Jakarta": (-6.2088, 106.8456),
    "Medan": (3.5952, 98.6722),
    "Surabaya": (-7.2575, 112.7521),
    "Bali": (-8.3405, 115.0920),
    "Palembang": (-2.9909, 104.7566),
    "Bandung": (-6.9175, 107.6191),
    "Makassar": (-5.1477, 119.4327),
    "Yogyakarta": (-7.7956, 110.3695),
    "Semarang": (-6.9666, 110.4167),
    "Pekanbaru": (0.5071, 101.4478),
    
    # Kalimantan (Borneo) cities
    "Pontianak": (0.0236, 109.3337),  # West Kalimantan
    "Banjarmasin": (-3.3190, 114.5902),  # South Kalimantan
    "Balikpapan": (-1.2707, 116.9019),  # East Kalimantan
    "Samarinda": (-0.5022, 117.1500),  # East Kalimantan
}

@st.cache_data
def load_data():
    # Rename columns
    columns = {
        'ocorrencia_classificacao': 'classificacao',
        'ocorrencia_tipo': 'tipo',
        'ocorrencia_tipo_categoria': 'tipo_categoria',
        'ocorrencia_tipo_icao': 'icao',
        'ocorrencia_latitude': 'latitude',
        "ocorrencia_longitude": 'longitude',
        'ocorrencia_cidade': 'cidade',
        'ocorrencia_uf': 'estado',
        'ocorrencia_pais': 'pais',
        'ocorrencia_aerodromo': 'aerodromo',
        'ocorrencia_dia': 'dia',
        'ocorrencia_horario': 'horario',
    }
    df = pd.read_csv(DATA_URL, index_col='codigo_ocorrencia')
    df.rename(columns=columns, inplace=True)
    df.dia = df.dia + ' ' + df.horario
    df.dia = pd.to_datetime(df.dia)
    df = df[list(columns.values())]
    return df

def map_to_cities(df: pd.DataFrame, cities: dict) -> pd.DataFrame:
    """
    Map accident locations to be closer to major Indonesian cities including Kalimantan.
    """
    # Get city names and their coordinates
    city_names = list(cities.keys())
    city_coords = np.array(list(cities.values()))

    # Assign each accident to a random city, with some small random offset
    random_city_indices = np.random.choice(len(city_names), size=len(df))
    df['cidade'] = [city_names[i] for i in random_city_indices]
    df['latitude'] = [
        city_coords[i][0] + np.random.uniform(-0.5, 0.5) for i in random_city_indices
    ]
    df['longitude'] = [
        city_coords[i][1] + np.random.uniform(-0.5, 0.5) for i in random_city_indices
    ]

    # Update the country to "Indonesia"
    df['pais'] = "Indonesia"
    return df

# Load and process data
df = load_data()
df = map_to_cities(df, INDONESIA_CITIES)

# Sidebar
st.sidebar.header('Parameters')
amount_data_shown = st.sidebar.empty()

st.sidebar.subheader('Year')
year_to_filter = st.sidebar.slider('Select the desired year:', 2008, 2018, 2017)

st.sidebar.subheader('Table')
# show_data = st.sidebar.checkbox('Show csv data')

multi_select_box = st.sidebar.multiselect(
    options=df['classificacao'].unique(),
    label="Choose the occurrences' classification",
    default=['ACIDENTE'],
)

df_filtered = df[(df.dia.dt.year == year_to_filter) & (df.classificacao.isin(multi_select_box))]

amount_data_shown.info(f"{df_filtered.shape[0]} selected occurrences")

# Main
st.title('Aeronautical Accidents In Indonesia')

# if show_data:
#     st.write(df_filtered)

st.subheader('Map of Occurrences')

# Map visualization
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(
        latitude=-2.5489,
        longitude=118.0149,
        zoom=4,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=df_filtered,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=50000,
        ),
    ],
))
