import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/carlosfab/curso_data_science_na_pratica/master/modulo_02/ocorrencias_aviacao.csv"

@st.cache

def load_data():
    """
        Carrega os dados de ocorrências aeronáuticas do CENIPA.

        :return: DataFrame com colunas selecionadas.
    """

    columns = {
        'ocorrencia_latitude': 'latitude',
        'ocorrencia_longitude': 'longitude',
        'ocorrencia_dia': 'data',
        'ocorrencia_classificacao': 'classificacao',
        'ocorrencia_tipo': 'tipo',
        'ocorrencia_tipo_categoria': 'tipo_categoria',
        'ocorrencia_tipo_icao': 'tipo_icao',
        'ocorrencia_aerodromo': 'aerodromo',
        'ocorrencia_cidade': 'cidade',
        'investigacao_status': 'status',
        'divulgacao_relatorio_numero': 'relatorio_numero',
        'total_aeronaves_envolvidas': 'aeronaves_envolvidas'
    }

    df = pd.read_csv(DATA_URL, index_col='codigo_ocorrencia')
    df.rename(columns=columns, inplace=True)
    date = df.data
    df.data = date + ' ' + df.ocorrencia_horario
    df['data'] = pd.to_datetime(df.data)
    df = df[list(columns.values())]
    return df

#load data
df = load_data()
labels = df.classificacao.unique().tolist()

# SIDEBAR
# Parameters and number of occurrences
st.sidebar.header('Parameters')
info_sidebar = st.sidebar.empty() # placeholder for later

# Slider for year selection
st.sidebar.subheader('Year')
year_to_filter = st.sidebar.slider('Select the desired year',2008, 2018, 2017)

# Table's checkbox
st.sidebar.subheader('Table')
table = st.sidebar.empty() # placeholder for later, it will be used with df_filtered

# Multiselection with labels
label_to_filter = st.sidebar.multiselect(
    label="Choose the occurrence's classification:",
    options=labels,
    default=["INCIDENTE", 'ACIDENTE']
)

# footer info
st.sidebar.markdown("""
The database of aeronautical events is managed by the 
***Center for Investigation and Prevention of Aeronautical Accidents (CENIPA)***.
""")

# Filtered data will be updated in our DataFrame
df_filtered = df[(df.data.dt.year == year_to_filter) & (df.classificacao.isin(label_to_filter))]

#  The empty placeholder is filled with df_filtered
info_sidebar.info("{} selected occurrences.".format(df_filtered.shape[0]))

# MAIN

st.title("CENIPA - Aeronautical Accidents")
st.markdown(f"""
            ℹ️ The occurrences shown below are classified as **{", ".join(label_to_filter)}**
            for the year of **{year_to_filter}**.
            """)

# raw data (table) depending on the checkbox
if table.checkbox("Show csv data"):
    st.write(df_filtered)

# map
st.subheader('Map of Occurrence')
st.map(df_filtered)