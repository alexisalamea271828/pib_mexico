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

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

#------------------------------------------------------------------------------------------------#
# IMPORTACIÓN DE LA BASE DE DATOS
archivo = 'Ejercicio Ingeniero de datos.xlsx'

@st.cache_data
def import_data(archivo):
    df = pd.read_excel(archivo, sheet_name='Ejercicio 1', header = 4)
    return df

df = import_data(archivo)    
df = df.rename(columns={'2015p/': 2015})

# Informaciónn adicional de la consulta de la base de datos
fuente = df.iloc[135, 0]
fuente = fuente[7:]
fecha_consulta = df.iloc[137, 0]
fecha_consulta = fecha_consulta[19:]  

#------------------------------------------------------------------------------------------------#
# TRANSFORMACIÓN DE LOS DATOS
# Redefinición del dataframe
df = df.iloc[:132,:]

# Crosstable
df = pd.melt(df, id_vars=['Actividad económica', 'Entidad','Concepto'], 
                    value_vars=[2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],
                    ignore_index=True,
                    var_name='Año', 
                    value_name='PIB')

# Cambiar el formato a la columna año
df['Año'] = df['Año'].astype('int64')

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
    
    sidebar.image('INEGI_3.jpg')
    sidebar.header('Producto Interno Bruto en México \n `2003 - 2016`')
    
    # Mostrar las primeras filas del dataframe
    st.write(df)