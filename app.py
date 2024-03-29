# Importación de librerías
import pandas as pd
import streamlit as st

# Lectura del archivo
archivo = 'Ejercicio Ingeniero de datos.xlsx'
df = pd.read_excel(archivo, sheet_name='Ejercicio 1', header = 4)
df = df.rename(columns={'2015p/': '2015'})

# Mostrar las primeras filas del dataframe
st.write(df)