# Importación de librerías
import pandas as pd
import streamlit as st

# Lectura del archivo
archivo = 'Ejercicio Ingeniero de datos.xlsx'
df = pd.read_excel(archivo, sheet_name='Ejercicio 1', header = 4)
df = df.rename(columns={'2015p/': 2015})

# Crosstable
df = pd.melt(df, id_vars=['Actividad económica', 'Entidad','Concepto'], 
                    value_vars=[2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],
                    ignore_index=True,
                    var_name='Año', 
                    value_name='PIB')

# Mostrar las primeras filas del dataframe
st.write(df)