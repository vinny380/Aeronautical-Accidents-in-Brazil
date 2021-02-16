# Importing modules
import streamlit as st
import pandas as pd
import pydeck as pdk

# dataset url
DATA_URL = "https://raw.githubusercontent.com/carlosfab/curso_data_science_na_pratica/master/modulo_02/ocorrencias_aviacao.csv"

@st.cache
# This function will load our data
def load_data():
    # Dict for changing the column labels
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
    df = pd.read_csv(DATA_URL, index_col='codigo_ocorrencia') # opening our dataset
    df.rename(columns=columns, inplace=True) # changing the name by using our dict
    df.dia = df.dia + ' ' + df.horario # merging the date and time labels
    df.dia = pd.to_datetime(df.dia) # casting the date + time label to_datetime()
    df = df[list(columns.values())] # listing our labels
    return df # returning our df

# Loading the data
df = load_data() # loading our dataset
labels = list(df.classificacao.unique()) # getting the values inside classificacao

# Side bar
st.sidebar.header('Parameters') # Sidebar title
amount_data_shown = st.sidebar.empty() # placeholder for later

st.sidebar.subheader('Year') # Sidebar subheader
year_to_filter = st.sidebar.slider('Select the desired year:', 2008, 2018, 2017) # Slider bar

st.sidebar.subheader('Table') # Subheader
show_data = st.sidebar.checkbox('Show csv data') # Checkbox for showing our dataset as a sheet our not

multi_select_box = st.sidebar.multiselect(  # Multiselection of classificacao values for our map
    options=labels,
    label="Choose the occurrences's classification",
    default=['ACIDENTE'],
)

df_filtered = df[(df.dia.dt.year == year_to_filter) & (df.classificacao.isin(multi_select_box))] # Filtering data

amount_data_shown.info("{} selected occurrences".format(df_filtered.shape[0])) # Amount of data shown

st.sidebar.markdown("""
The database of aeronautical events is managed by the 
***Center for Investigation and Prevention of Aeronautical Accidents (CENIPA)***.
""") # Sidebar footer

# MAIN
st.title('CENIPA - Aeronautical Accidents') # Main title

if show_data: # If our checkbox is selected, display our dataset
    st.write(df_filtered)

sub = st.markdown('ℹ️ The occurrences shown below are classified as **{}** for the year of **{}**.'
                  .format(', '.join(multi_select_box), year_to_filter)) # Subtitle text

# MAP with pydeck
st.subheader('**Map of Occurrences**')
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(
        latitude=-12.979082,
        longitude=-54.7514481,
        zoom=3,
        pitch=50,
    ),
    layers=[
        pdk.Layer( # Heatmap layer first
            'HeatmapLayer',
            data=df_filtered,
            opacity=2,
            radius=30000,
            get_position='[longitude, latitude]',
            auto_highlight=True,
            threshold=1,
            pickable=True,
            extruded=True,
        ),
        pdk.Layer( # A grid layer above
            'GridLayer',
            data=df_filtered,
            get_position='[longitude, latitude]',
            get_radius=68800,
            pickable=True,
            extruded=True,
            cell_size=40000,
            elevation_scale=1500,
        ),
    ]
))