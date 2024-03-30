# Importación de librerías
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pydeck as pdk
#from pydeck import Layer, ViewState

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

#------------------------------------------------------------------------------------------------#
# IMPORTACIÓN DE LA BASE DE DATOS
archivo = 'Ejercicio Ingeniero de datos.xlsx'

@st.cache_data
def import_data(archivo):
    df_original = pd.read_excel(archivo, sheet_name='Ejercicio 1', header = 4)
    return df_original

df_original = import_data(archivo)    
df_original = df_original.rename(columns={'2015p/': 2015})

# Informaciónn adicional de la consulta de la base de datos
fuente = df_original.iloc[135, 0]
fuente = fuente[7:]
fecha_consulta = df_original.iloc[137, 0]
fecha_consulta = fecha_consulta[19:]  

# Información sobre los estados: latitud y longitud
informacion_estados = pd.read_csv("Latitud y longitud de los estados.txt", sep=",")
informacion_estados = informacion_estados.sort_values(by="Entidad")
informacion_estados = informacion_estados.reset_index(drop=True)

#------------------------------------------------------------------------------------------------#
# TRANSFORMACIÓN DE LOS DATOS
# Redefinición del dataframe
df_original = df_original.iloc[:132,:]

# Crosstable
df_original = pd.melt(df_original, id_vars=['Actividad económica', 'Entidad','Concepto'], 
                    value_vars=[2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],
                    ignore_index=True,
                    var_name='Año', 
                    value_name='PIB')

# Cambiar el formato a la columna año
df_original['Año'] = df_original['Año'].astype('int64')

# Quitar los espacios en blanco al inicio y al final de la columna de entidades
df_original['Entidad'] = df_original['Entidad'].str.strip()

# Unión con la latitud y longitud de los estados
df_original.merge(informacion_estados, on='Entidad', how='left')

df = df_original[['Actividad económica', 'Entidad','Año','PIB']]

#------------------------------------------------------------------------------------------------#
#------- Menú de navegación ----------
option_selected = option_menu(
	menu_title=None,
	options=["Analisis general", "Análisis por estado", "Sobre los indicadores"],
    orientation="horizontal"
)
    # SIDEBAR
sidebar = st.sidebar

if option_selected == "Analisis general":
    
    df = df[df["Entidad"] == "Total nacional"]

    sidebar.image('INEGI_3.jpg')
    sidebar.header('Producto Interno Bruto en México \n `2003 - 2016`')
    
    años = df['Año'].unique()
    entidades = df['Entidad'].unique()

    col1, col2, col3, col4 = st.columns((1,3,3,1))

    años_seleccionados = col2.multiselect("Año: ", años, default=[2003])
    entidad_seleccionada = col3.selectbox("Entidad: ", entidades)

    df_analisis_general = df[df['Año'].isin(años_seleccionados)]
    df_analisis_general = df_analisis_general[df_analisis_general["Entidad"] == entidad_seleccionada]

    # Mostrar las primeras filas del dataframe
    st.write(df_analisis_general)

    # Mapa
    chart_data = df_original

    # 2014 locations of car accidents in the UK
    UK_ACCIDENTS_DATA = ('https://raw.githubusercontent.com/uber-common/'
                        'deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv')

    # Define a layer to display on a map
    layer = pdk.Layer(
        'HexagonLayer',
        chart_data,
        get_position=['Longitud', 'Latitud'],
        auto_highlight=True,
        elevation_scale=50,
        pickable=True,
        elevation_range=[0, 3000],
        extruded=True,                 
        coverage=1)

    # Set the viewport location
    view_state = pdk.ViewState(
        longitude=-1.415,
        latitude=52.2323,
        zoom=6,
        min_zoom=5,
        max_zoom=15,
        pitch=40.5,
        bearing=-27.36)

    # Render
    r = pdk.Deck(layers=[layer], initial_view_state=view_state)
    r.to_html('demo.html', notebook_display=False)
    
    st.write(r)

elif option_selected == "Análisis por estado":

    df = df[df["Entidad"] != "Total nacional"]

    sidebar.image('INEGI_3.jpg')
    sidebar.header('Producto Interno Bruto en México \n `2003 - 2016`')
    
    años = df['Año'].unique()
    entidades = df['Entidad'].unique()
    actividades_economicas = df['Actividad económica'].unique()

    col1, col2, col3, col4 = st.columns((1,4,4,1))
    col5, col6, col7, col8 = st.columns((1,4,4,1))

    año_inicial_seleccionado = col2.selectbox("Año inicial: ", años[:-1])
    años_2 = años[años >= año_inicial_seleccionado]
    año_final_seleccionado = col3.selectbox("Año final: ", años_2, index = 1)
    
    entidad_seleccionada = col6.selectbox("Entidad: ", entidades)
    actividades_economicas_seleccionadas = col7.multiselect("Actividades económicas: ", actividades_economicas, 
                                            default = ["Actividades primarias", "Actividades secundarias", "Actividades terciarias"])

    df_analisis_estado = df[(df['Año'] >= año_inicial_seleccionado) & (df['Año'] <= año_final_seleccionado)]
    df_analisis_estado = df_analisis_estado[df_analisis_estado["Entidad"] == entidad_seleccionada]
    df_analisis_estado = df_analisis_estado[df_analisis_estado["Actividad económica"].isin(actividades_economicas_seleccionadas)]

    # Mostrar las primeras filas del dataframe
    st.write(df_analisis_estado)

    # Mostrar las primeras filas del dataframe
    chart_data = df_analisis_estado
    #st.line_chart(chart_data, x="Año", y="PIB", color="Actividad económica", width = 100, height = 800)
    fig = px.area(chart_data, x="Año", y="PIB", log_y = True, 
                    color="Actividad económica", 
                    markers = True,
                    title="Comportamiento del PIB de {} a través del tiempo".format(entidad_seleccionada))
    
    col1, col2, col3 = st.columns((1,6,1))
    col2.write(fig)