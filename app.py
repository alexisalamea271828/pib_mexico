# Importación de librerías
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from streamlit_kpi import streamlit_kpi
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

# Información sobre el país: población
informacion_poblacion = pd.read_excel("Population.xlsx")
informacion_poblacion = informacion_poblacion[["Country name", "Year", "Population"]]
informacion_poblacion = informacion_poblacion[(informacion_poblacion["Year"]>=2003)&(informacion_poblacion["Year"]<=2016)].reset_index(drop=True)
informacion_poblacion["Country name"].replace({"Mexico": "Total nacional"}, inplace=True)

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
    chart_data_nacional = df_original[df_original["Entidad"] == "Total nacional"]

    # Unión con la latitud y longitud de los estados
    chart_data_nacional = chart_data_nacional.merge(informacion_poblacion, left_on="Año", right_on="Year", how='left')
    chart_data_nacional = chart_data_nacional.assign(PIB_per_capita = lambda x: ((x["PIB"]/x["Population"])*1000000))
    chart_data_nacional_sin_filtro = chart_data_nacional

    sidebar.image('INEGI_3.jpg')
    sidebar.header('Producto Interno Bruto en México \n `2003 - 2016`')
    
    años = df['Año'].unique()
    entidades = df['Entidad'].unique()

    # Explicación
    with st.expander("Ver información"):
        st.write('''En el siguiente filtro seleccione un año entre 2003 y 2016. Los KPIs mostrarán los valores de: \n
        * Valor del PIB nacional y una comparación del año seleccionado con el del año 2003.\n 
        * Valor del PIB per cápita nacional y una comparación del año seleccionado con el del año 2003. \n
        ''')
    
    col1, col2, col3 = st.columns((1,6,1))

    # Filtros
    año_seleccionado = col2.selectbox("Año a comparar: ", años)

    chart_data = chart_data[chart_data['Año'] == año_seleccionado]
    chart_data_nacional_2003 = chart_data_nacional[chart_data_nacional['Año'] == 2003]
    chart_data_nacional = chart_data_nacional[chart_data_nacional['Año'] == año_seleccionado]

    PIB_nacional = chart_data_nacional[chart_data_nacional["Concepto"] == "Total nacional -Total de la actividad económica"]["PIB"].reset_index(drop=True)[0]
    PIB_nacional_2003 = chart_data_nacional_2003[chart_data_nacional_2003["Concepto"] == "Total nacional -Total de la actividad económica"]["PIB"].reset_index(drop=True)[0]
    
    PIB_per_capita_nacional = chart_data_nacional[chart_data_nacional["Concepto"] == "Total nacional -Total de la actividad económica"]["PIB_per_capita"].reset_index(drop=True)[0]
    PIB_per_capita_nacional_2003 = chart_data_nacional_2003[chart_data_nacional_2003["Concepto"] == "Total nacional -Total de la actividad económica"]["PIB_per_capita"].reset_index(drop=True)[0]

    delta_PIB_nacional = (PIB_nacional - PIB_nacional_2003)/PIB_nacional_2003
    delta_PIB_per_capita_nacional = (PIB_per_capita_nacional - PIB_per_capita_nacional_2003)/PIB_per_capita_nacional_2003
    
    col1, col2, col3, col4 = st.columns((1,5,5,1))
    col2.metric(label="PIB nacional en {} en millones de pesos".format(año_seleccionado), 
                    value = "${:,.2f}".format(PIB_nacional),
                    delta = "{:.2%} vs año 2003".format(delta_PIB_nacional))

    col3.metric(label="PIB per cápita nacional en {} en pesos".format(año_seleccionado), 
                    value = "${:,.2f}".format(PIB_per_capita_nacional),
                    delta = "{:.2%} vs año 2003".format(delta_PIB_per_capita_nacional))
    
    # Explicación
    with st.expander("Ver información"):
        st.write('''En el siguiente contenedor observará 5 pestañas que mostrarán una gráfica de área que representa
        el comportamiento del PIB en la categoría seleccionada a través del tiempo. Esta información no depende del filtro de año. 
        ''')

    # Gráficos de área por categoría
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["PIB", 
                                            "Actividades primarias", 
                                            "Actividades secundarias",
                                            "Actividades terciarias",
                                            "PIB per cápita"])

    with tab1:
        chart_data_1 = chart_data_nacional_sin_filtro[chart_data_nacional_sin_filtro["Actividad económica"] == "Total de la actividad económica"]
        fig1 = px.area(chart_data_1, x="Año", y="PIB", log_y = False, 
                    #color="PIB", 
                    markers = True,
                    title="Comportamiento del PIB nacional a través del tiempo")
        col1, col2, col3 = st.columns((1,6,1))
        col2.write(fig1)

    with tab2:
        chart_data_2 = chart_data_nacional_sin_filtro[chart_data_nacional_sin_filtro["Actividad económica"] == "Actividades primarias"]
        fig2 = px.area(chart_data_2, x="Año", y="PIB", log_y = False, 
                    #color="PIB", 
                    markers = True,
                    title="Comportamiento del PIB nacional representado por actividades primarias a través del tiempo")
        col1, col2, col3 = st.columns((1,6,1))
        col2.write(fig2)

    with tab3:
        chart_data_3 = chart_data_nacional_sin_filtro[chart_data_nacional_sin_filtro["Actividad económica"] == "Actividades secundarias"]
        fig3 = px.area(chart_data_3, x="Año", y="PIB", log_y = False, 
                    #color="PIB", 
                    markers = True,
                    title="Comportamiento del PIB nacional representado por actividades secundarias a través del tiempo")
        col1, col2, col3 = st.columns((1,6,1))
        col2.write(fig3)
    
    with tab4:
        chart_data_4 = chart_data_nacional_sin_filtro[chart_data_nacional_sin_filtro["Actividad económica"] == "Actividades terciarias"]
        fig4 = px.area(chart_data_4, x="Año", y="PIB", log_y = False, 
                    #color="PIB", 
                    markers = True,
                    title="Comportamiento del PIB nacional representado por actividades terciarias a través del tiempo")
        col1, col2, col3 = st.columns((1,6,1))
        col2.write(fig4)

    with tab5:
        chart_data_5 = chart_data_nacional_sin_filtro[chart_data_nacional_sin_filtro["Actividad económica"] == "Total de la actividad económica"]
        fig5 = px.area(chart_data_5, x="Año", y="PIB_per_capita", log_y = False, 
                    #color="PIB", 
                    markers = True,
                    title="Comportamiento del PIB per cápita nacional a través del tiempo")
        col1, col2, col3 = st.columns((1,6,1))
        col2.write(fig5)

    # Explicación
    with st.expander("Ver información"):
        st.write('''En el siguiente mapa de México se ubica el valor del PIB por estado para TODAS LAS ACTVIDADES ECONÓMICAS.
        Cada punto se ubicó en la capital de cada uno de los estados, a través de su latitud y longitud. El color y el tamaño del punto
        nos dice qué tan alto o bajo es el valor del PIB en dicho estado. 
        Esta información SÍ depende del año seleccionado. 
        ''')

    # Mapa
    st.markdown('''<h1 style='font-size: 1.7rem; text-align:center; color: #DAF7A6;'>PIB por estado en {}</h1>'''.format(año_seleccionado), unsafe_allow_html=True)

    fig = px.scatter_mapbox(chart_data, 
                            lat="Latitud", 
                            lon="Longitud", 
                            hover_name="Entidad", 
                            hover_data=["Entidad", "PIB"],
                            color="PIB",
                            color_continuous_scale=px.colors.cyclical.IceFire, 
                            size_max=20,
                            size="PIB",
                            zoom=3.65, 
                            height=400,
                            width=800)
    
    fig.update_layout(mapbox_style="open-street-map",
                    title='PIB por estado en {}'.format(año_seleccionado),
                    autosize=True,
                    hovermode='closest',
                    mapbox=dict(
                        bearing=0,
                        center=dict(
                            lat = 24,
                            lon = -102
                        )))

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    col1, col2, col3 = st.columns((1,6,1))
    col2.write(fig)

    chart_data.sort_values(by = "PIB", inplace = True)
    
    # Explicación
    with st.expander("Ver información"):
        st.write('''A continuación se muestra el top 5 de los estados con mayor PIB en el año seleccionado. 
        Se considera la información de TODAS LAS ACTIVIDADES ECONÓMICAS, no está desglosada una a una.
        ''')

    # TOP 5 de estados por PIB
    st.markdown('''<h1 style='font-size: 1.7rem; text-align:center; color: #DAF7A6;'>Top 5 de estados en {}</h1>'''.format(año_seleccionado), unsafe_allow_html=True)
    col1, col2, col3 = st.columns((1,6,1))
    progress_chart_column = chart_data[chart_data["Actividad económica"]=='Total de la actividad económica']
    progress_chart_column.sort_values(by = "PIB", ascending = False, inplace = True)
    progress_chart_column = progress_chart_column.iloc[:5,:]
    col2.dataframe(progress_chart_column,
                column_order=("Entidad", "PIB"),
                hide_index=True,
                width=None,
                column_config={
                    "Entidad": st.column_config.TextColumn(
                        "Entidad",
                    ),
                    "PIB": st.column_config.ProgressColumn(
                        "PIB",
                        format="$ %.2f",
                        min_value=0,
                        max_value=max(progress_chart_column.PIB),
                    )}
                )

    # Explicación
    with st.expander("Ver información"):
        st.write('''El siguiente gráfico es continuación del anterior. En este se muestran gráficas de barras con la información del PIB de los estados en el año seleccionado.
        Se presenta un análisis para:  \n 1) TODAS LAS ACTIVIDADES ECONÓMICAS. \n 2) Actividades primarias.
        \n 3) Actividades secundarias. \n 4) Actividades terciarias.
        ''')

    # Gráfico de barras por tipo de actividad económica
    st.markdown('''<h1 style='font-size: 1.7rem; text-align:center; color: #DAF7A6;'>Analisis por tipo de actividad económica en {}</h1>'''.format(año_seleccionado), unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Todas las atividades", 
                                            "Actividades primarias", 
                                            "Actividades secundarias",
                                            "Actividades terciarias"])

    with tab1:
        chart_data_bar_chart_1 = chart_data[chart_data["Actividad económica"]=='Total de la actividad económica']
        fig_bar_chart_1 = px.bar(chart_data_bar_chart_1, y='Entidad', x='PIB',
                hover_data=['Entidad', 'PIB', 'Actividad económica'], 
                color='Actividad económica',
                color_discrete_sequence=["orange"],
                orientation="h",
                height=600)
        col1, col2, col3 = st.columns((1,6,1))
        col2.write(fig_bar_chart_1)

    with tab2:
        chart_data_bar_chart_2 = chart_data[chart_data["Actividad económica"]=='Actividades primarias']
        fig_bar_chart_2 = px.bar(chart_data_bar_chart_2, y='Entidad', x='PIB',
                hover_data=['Entidad', 'PIB', 'Actividad económica'], 
                color='Actividad económica',
                color_discrete_sequence=["orange"],
                orientation="h",
                height=600)
        col1, col2, col3 = st.columns((1,6,1))
        col2.write(fig_bar_chart_2)

    with tab3:
        chart_data_bar_chart_3 = chart_data[chart_data["Actividad económica"]=='Actividades secundarias']
        fig_bar_chart_3 = px.bar(chart_data_bar_chart_3, y='Entidad', x='PIB',
                hover_data=['Entidad', 'PIB', 'Actividad económica'], 
                color='Actividad económica',
                color_discrete_sequence=["orange"],
                orientation="h",
                height=600)
        col1, col2, col3 = st.columns((1,6,1))
        col2.write(fig_bar_chart_3)
    
    with tab4:
        chart_data_bar_chart_4 = chart_data[chart_data["Actividad económica"]=='Actividades terciarias']
        fig_bar_chart_4 = px.bar(chart_data_bar_chart_4, y='Entidad', x='PIB',
                hover_data=['Entidad', 'PIB', 'Actividad económica'], 
                color='Actividad económica',
                color_discrete_sequence=["orange"],
                orientation="h",
                height=600)
        col1, col2, col3 = st.columns((1,6,1))
        col2.write(fig_bar_chart_4)

elif option_selected == "Análisis por estado":

    df_0 = df[df["Entidad"] == "Total nacional"]
    df = df[df["Entidad"] != "Total nacional"]

    sidebar.image('INEGI_3.jpg')
    sidebar.header('Producto Interno Bruto en México \n `2003 - 2016`')
    
    años = df['Año'].unique()
    entidades = df['Entidad'].unique()
    actividades_economicas = df['Actividad económica'].unique()

    # Explicación
    with st.expander("Ver información"):
        st.write('''A continuación de muestra un conjunto de filtros que permiten seleccionar un año entre 2003 y 2016, una de las 31 entidades federativas (o la Ciudad de México, antes D.F.) y el tipo de actividad económica.
        Los KPIs mostrarán los valores de:\n
        * El mayor PIB registrado en el estado seleccionado entre 2003 y 2016 (así como el año en el que se presentó).\n 
        * El mayor incremento de PIB registrado en el estado seleccionado, comparado con el año previo, entre 2004 y 2016 (así como el año en el que se presentó). \n
        * Porcentaje que representa del PIB Nacional el PIB del estado seleccionado, en el año seleccionado, por cada tipo de actividad económica (hay 3).\n
        ''')

    col1, col2, col3, col4 = st.columns((1,4,4,1))
    col5, col6, col7 = st.columns((1,8,1))

    año_final_seleccionado = col2.selectbox("Año final: ", años, index = 1)
    
    entidad_seleccionada = col3.selectbox("Entidad: ", entidades)
    actividades_economicas_seleccionadas = col6.multiselect("Actividades económicas: ", actividades_economicas, 
                                            default = ["Actividades primarias", "Actividades secundarias", "Actividades terciarias"])

    df_analisis_estado = df[df['Año'] <= año_final_seleccionado]
    df_analisis_estado = df_analisis_estado[df_analisis_estado["Entidad"] == entidad_seleccionada]
    df_analisis_estado = df_analisis_estado[df_analisis_estado["Actividad económica"].isin(actividades_economicas_seleccionadas)]

    # Creación de la columna de incremento en el PIB anual respecto al anterior
    chart_data_estado = df[df["Entidad"] == entidad_seleccionada]
    chart_data_estado = chart_data_estado[chart_data_estado["Actividad económica"]=="Total de la actividad económica"]

    chart_data_estado.reset_index(drop=True, inplace=True)
    for i in range(1,chart_data_estado["Año"].shape[0]):
        a_1 = chart_data_estado.loc[i-1,"PIB"]
        a_2 = chart_data_estado.loc[i,"PIB"]
        chart_data_estado.loc[i,"delta_PIB"] = ((a_2 - a_1)/a_1)
        chart_data_estado.loc[i,"delta_PIB [porcentaje]"] = ((a_2 - a_1)/a_1)*100

    chart_data_estado_sin_2003 = chart_data_estado[chart_data_estado["Año"] != 2003]

    # Creación de los KPIs
    # KPI 1: PIB registrado en la entidad
    chart_data_estado_pib_sorted = chart_data_estado.sort_values(by = "PIB", ascending = False, inplace = False)
    chart_data_estado_pib_sorted.reset_index(drop=True, inplace=True)
    kpi_1 = chart_data_estado_pib_sorted.loc[0,"PIB"]
    año_1 = chart_data_estado_pib_sorted.loc[0,"Año"]
    
    # KPI 2: Incremento del PIB
    chart_data_estado_delta_pib_sorted = chart_data_estado_sin_2003.sort_values(by = "delta_PIB", ascending = False, inplace = False)
    chart_data_estado_delta_pib_sorted.reset_index(drop=True, inplace=True)
    kpi_2 = chart_data_estado_delta_pib_sorted.loc[0,"delta_PIB"]
    año_2 = chart_data_estado_delta_pib_sorted.loc[0,"Año"]

    # Nacional
    chart_data_nacional_kpi_3 = df_0[df_0["Año"]== año_final_seleccionado]
    chart_data_nacional_kpi_3 = chart_data_nacional_kpi_3[chart_data_nacional_kpi_3["Actividad económica"] == "Total de la actividad económica"]
    chart_data_nacional_kpi_3.reset_index(drop=True, inplace=True)
    kpi_nacional = chart_data_nacional_kpi_3.loc[0,"PIB"]

    # KPI 3: Porcentaje del PIB nacional por actividades primarias
    # Estado
    chart_data_estado_kpi_3 = df[df["Año"]== año_final_seleccionado]
    chart_data_estado_kpi_3 = chart_data_estado_kpi_3[chart_data_estado_kpi_3["Actividad económica"] == "Actividades primarias"]
    chart_data_estado_kpi_3 = chart_data_estado_kpi_3[chart_data_estado_kpi_3["Entidad"] == entidad_seleccionada]
    chart_data_estado_kpi_3.reset_index(drop=True, inplace=True)
    kpi_3_estado = chart_data_estado_kpi_3.loc[0,"PIB"]
    #Porcentaje
    kpi_3 = kpi_3_estado/kpi_nacional

    # KPI 4: Porcentaje del PIB nacional por actividades secundarias
    # Estado
    chart_data_estado_kpi_4 = df[df["Año"]== año_final_seleccionado]
    chart_data_estado_kpi_4 = chart_data_estado_kpi_4[chart_data_estado_kpi_4["Actividad económica"] == "Actividades secundarias"]
    chart_data_estado_kpi_4 = chart_data_estado_kpi_4[chart_data_estado_kpi_4["Entidad"] == entidad_seleccionada]
    chart_data_estado_kpi_4.reset_index(drop=True, inplace=True)
    kpi_4_estado = chart_data_estado_kpi_4.loc[0,"PIB"]
    #Porcentaje
    kpi_4 = kpi_4_estado/kpi_nacional

    # KPI 5: Porcentaje del PIB nacional por actividades terciarias
    # Estado
    chart_data_estado_kpi_5 = df[df["Año"]== año_final_seleccionado]
    chart_data_estado_kpi_5 = chart_data_estado_kpi_5[chart_data_estado_kpi_5["Actividad económica"] == "Actividades terciarias"]
    chart_data_estado_kpi_5 = chart_data_estado_kpi_5[chart_data_estado_kpi_5["Entidad"] == entidad_seleccionada]
    chart_data_estado_kpi_5.reset_index(drop=True, inplace=True)
    kpi_5_estado = chart_data_estado_kpi_5.loc[0,"PIB"]
    #Porcentaje
    kpi_5 = kpi_5_estado/kpi_nacional
    
    st.markdown(" ")
    col1, col2, col3, col4 = st.columns((1,5,5,1))
    col2.metric(label="Mayor PIB registrado en millones de pesos", 
                    value = año_1,
                    delta = "${:,.2f}".format(kpi_1)
                    )
    col3.metric(label="Mayor incremento de PIB entre 2003 y 2016", 
                    value = año_2,
                    delta = "{:.2%}".format(kpi_2)
                    )
    st.markdown('''<h1 style='font-size: 1.0rem; text-align:center; color: #DAF7A6;'>Porcentaje del PIB de {} respecto al PIB nacional por tipo de actividad:</h1>'''.format(entidad_seleccionada), unsafe_allow_html=True)
    column1, column2, column3, column4, coolumn5 = st.columns((1,5,5,5,1))
    column2.metric(label="Actividades primarias", value = "{:.2%}".format(kpi_3))
    column3.metric(label="Actividades secundarias", value = "{:.2%}".format(kpi_4))
    column4.metric(label="Actividades terciarias", value = "{:.2%}".format(kpi_5))

    # Explicación
    with st.expander("Ver información"):
        st.write('''Gráfica que muestra el comportamiento del PIB del estado entre 2003 y el año seleccionado, 
        para las categorías de actividades económicas seleccionadas enn los filtros anteriores. 
        ''')

    # Gráfica de área de comportamiento del PIB a través del tiempo
    chart_data = df_analisis_estado
    fig = px.area(chart_data, x="Año", y="PIB", log_y = True, 
                    color="Actividad económica", 
                    markers = True,
                    title="Comportamiento del PIB de {} a través del tiempo por tipo de actividad económica".format(entidad_seleccionada))
    
    col1, col2, col3 = st.columns((1,6,1))
    col2.write(fig)

    # Explicación
    with st.expander("Ver información"):
        st.write('''Tabla que muestra los 3 años que tuvieron un mayor crecimiento de PIB comparado con el del año previo, para el estado seleccionado. 
        ''')

    # TOP 3 de años con mayor incremento del PIB
    st.markdown('''<h1 style='font-size: 1.5rem; text-align:center; color: #DAF7A6;'>Top 3 de años con mayor incremento de PIB (respecto al año anterior) en {}</h1>'''.format(entidad_seleccionada), unsafe_allow_html=True)
    col1, col2, col3 = st.columns((1,6,1))
    progress_chart_column = chart_data_estado_sin_2003
    progress_chart_column.sort_values(by = "delta_PIB", ascending = False, inplace = True)
    progress_chart_column = progress_chart_column.iloc[:3,:]
    col2.dataframe(progress_chart_column,
                column_order=("Año", "PIB","delta_PIB"),
                hide_index=True,
                width=None,
                column_config={
                    "Año": st.column_config.TextColumn(
                        "Año",
                        width="medium",
                    ),
                    "PIB": st.column_config.TextColumn(
                        "PIB",
                        width="medium",
                    ),
                    "delta_PIB": st.column_config.ProgressColumn(
                        "delta_PIB",
                        width="medium",
                        min_value=0,
                        max_value=max(progress_chart_column.delta_PIB),
                    )}
                )

    # Explicación
    with st.expander("Ver información"):
        st.write('''Gráfica de área que representa el comportamiento de la TASA DE CAMBIO del PIB con el paso de los años, para el estado seleccionado. 
        Esta gráfica no depende del filtro de año seleccionado.
        ''')

    # Gráfico de área para representar el cambio en el PIB año tras año
    fig_delta_PIB = px.area(chart_data_estado_sin_2003, x="Año", y="delta_PIB [porcentaje]", log_y = False, 
                #color="PIB", 
                markers = True,
                title="Comportamiento del incremento del PIB de {} a través del tiempo".format(entidad_seleccionada))
    columna1, columna2, columna3 = st.columns((1,6,2))
    columna2.write(fig_delta_PIB)

    # Explicación
    with st.expander("Ver información"):
        st.write('''Gráfica de pie que representa la proporción del PIB del estado en el año seleccionado por cada tipo de actividad económica.
        ''')

    # Gráfico de pie que representa la proporción del PIB por tipo de actividad
    df_aux = pd.DataFrame()
    df_aux["Tipo de actividad"] = ["Actividades primarias", "Actividades secundarias", "Actividades terciarias"]
    df_aux["PIB"] = [kpi_3_estado,kpi_4_estado,kpi_5_estado]
    fig_pie_chart = px.pie(df_aux, values='PIB', names='Tipo de actividad', 
                    color = ["#D6DBDF","#F1C40F","#D35400"],
                    title="Porcentaje del PIB en {} en {} por tipo de actividad".format(entidad_seleccionada, año_final_seleccionado))
    columna1, columna2, columna3 = st.columns((1,6,2))
    columna2.write(fig_pie_chart)

elif option_selected == "Sobre los indicadores":
    st.markdown('''Con el objetivo de tener una mejor visión del producto interno bruto de los estados del país, y del país en general, 
    se presenta un conjunto de gráficos y filtros que permiten analizar la información proporcionada. \n Para ello, se crearon dos pestañas en la presente aplicación: \n
    - Análisis general, que analiza la información a través de indicadores a NIVEL NACIONAL.
    - Análisis por estado, en el que se profundiza sobre la información que se tiene sobre cada ENTIDAD FEDERATIVA.\n Con lo anterior se permite 
    tener una analisis descriptivo de la información, como la obtención de los valores máximos del PIB y de PIB per cápita, los valores totales considerando todas las actividades económicas y/o estados, porcentajes, entre otras cosas. \n\n De manera
    muy particular, se proponen el siguiente set de indicadores para monitorear la situación del país y de los estados, y que podría permitirnos tomar decisiones más informadas y basadas en datos: \n
    Tasa de cambio del PIB respecto al año previo. Este indicador nos permite determinar si el valor de la producción de 
    bienes y servicios de demanda final en un estado o en el país ha incrementado o disminuido. Si bien el PIB es una 
    variable macroeconómica que depende de diversos factores, que se podrían relacionar con el progreso técnico, la inversión,
    la apertura de mercados, o incluso (de manera negativa) con desastres naturales que afectan la producción de miles de 
    habitantes, monitorear este indicador nos invitaría a preguntarnos cuáles son las causas que están impactando para que 
    este varíe y en qué medida ha estado afectando al país o estado. Por ejemplo, de acuerdo con los datos, el PIB de Campeche
    ha estado disminuyendo año tras año, a excepción del año 2004 y 2013. ¿Qué ha originado que el estado se encuentre en dicha
    situación? \n
    PIB per cápita. Como el PIB es una medida de la producción de bienes y servicios de demanda final, es lógico esperar que, 
    en la mayoría de los casos, una región con más habitantes tenga mayor PIB que otra con menos habitantes y con condiciones
    similares que favorezcan en la misma medida la producción de dichos bienes y servicios. Por esta razón, se propone monitorear
    el PIB per cápita, que es una medida del PIB de la región por persona. Es como si la riqueza de la región (país o estado) 
    se repartiera a todos por igual. En este sentido, medir el PIB per cápita permitiría tener una mejor comparación de la misma 
    región en años diferentes, o, por ejemplo, una comparación entre el PIB per cápita de un estado y otro en el mismo año.
    Si bien no se encontró una fuente que proporcionara la población anual por estado (solo había de los censos de la población
    que se realizaba cada cierta cantidad de años), sí se contró una con la población del país entre 2003 y 2016.
    Con esto, se obtenía que en 2016 a cada mexicano le hubiese correspondido $140,127.43 si la riqueza del país se 
    hubiese repartido a todos por igual, que al mismo tiempo fue un 14.28% mayor comparado con 2003.\n
    Contribución del PIB por tipo de actividad económica. Este indicador nos permitiría determinar qué tipo de
    actividades se llevan a cabo principalmente en cada país o región. Con esto, si se desea impulsar a un estado o al país
    a que mejore su PIB se podría ver qué tipo de soluciones se les podría brindar dependiendo de ello. Por ejemplo, si la mayor
    parte del PIB de un estado o país se basa en actividades relacionadas con el trasporte, el turismo o la comercialización
    de productos y servicios, puede que se deba a que su localización geográfica no le permita basar su economía en la producción
    de fresas o tomates. Entonces, no le sería de utilidad que se busque impulsar la agricultura porque las condiciones
    climatológicas no le favorecen, pero quizás sí le ayude que se invierta en los atractivos turísticos o la infraestructura
    de carreteras para que se sigan impulsando las actividades relacionadas con el transporte, tal es el caso de la ciudad de México,
    que en el 2016, solo el 0.06% de su PIB se debió a actividades primarias, pero el 86.6% se debió a actividades terciarias.\n\n
    




    ''')

# PIE DE PÁGINA
col1, col2, col3 = st.columns ((1,6,1))
col2.markdown("<h1 style='text-align: center; font-size: 1.0rem;'>©ÁNGEL ALEXIS ANAYA ALAMEA | TODOS LOS DERECHOS RESERVADOS</h1>", unsafe_allow_html=True)
col2.markdown("<h1 style='text-align: center; font-size: 0.8rem;'>Correo: angelalexisanayaalamea314@gmail.com</h1>", unsafe_allow_html=True)
    