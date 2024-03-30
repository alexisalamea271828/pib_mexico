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
informacion_estados = pd.read_excel("Latitud y longitud de los estados.xlsx")
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

# Sustituir valores de algunos estados
df_original['Entidad'].replace({'Michoacán de Ocampo': 'Michoacán',
                                                        'Veracruz de Ignacio de la Llave':'Veracruz',
                                                        'Coahuila de Zaragoza':'Coahuila'}, inplace=True)


# Unión con la latitud y longitud de los estados
df_original = df_original.merge(informacion_estados, on='Entidad', how='left')

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
    
    df = df[df["Entidad"] != "Total nacional"]
    chart_data = df_original[df_original["Entidad"] != "Total nacional"]
    #chart_data_pib_1000 = chart_data.loc[:"PIB"]/10000
    #chart_data.loc[:, "PIB/10000"] = chart_data_pib_1000s

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
    st.write(chart_data)
    #st.map(chart_data, latitude='Latitud', longitude='Longitud', size='PIB/10000')
    color_scale = [(0, '#0A2F51'), (1,'#39A96B')]
    fig = px.scatter_mapbox(chart_data, 
                            lat="Latitud", 
                            lon="Longitud", 
                            hover_name="Entidad", 
                            hover_data=["Entidad", "PIB"],
                            color="PIB",
                            color_continuous_scale=px.colors.cyclical.IceFire, 
                            size_max=15,
                            size="PIB",
                            zoom=3.5, 
                            height=400,
                            width=800)
    #open-street-map
    fig.update_layout(mapbox_style="light",
                    mapbox=dict(
                        bearing=0,
                        center=dict(
                            lat = 24,
                            lon = -102
                        )))

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.write(fig)

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