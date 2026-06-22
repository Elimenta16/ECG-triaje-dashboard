import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Dashboard de Triaje Clínico - ECG",
    page_icon="🏥",
    layout="wide"
)

# Título de la aplicación (Enfoque profesional y normativo)
st.title("🏥 Sistema de Triaje Clínico Automatizado (ECG)")
st.caption("Cumplimiento normativo de análisis de datos de salud en base a la NOM-004-SSA3-2012")
st.markdown("---")

# 1. Función para cargar los datos de manera eficiente
@st.cache_data
def cargar_datos():
    # Reemplaza con el nombre exacto de tu archivo CSV si es necesario
    try:
        df = pd.read_csv("ECG_dataset_100_patients.csv")
        return df
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo CSV. Asegúrate de que esté en la misma carpeta que este script.")
        return None

df = cargar_datos()

if df is not None:
    # 2. Algoritmo de Triaje Automatizado (Lógica Biomédica)
    # Aquí definimos reglas lógicas basadas en parámetros comunes (ej. Frecuencia Cardíaca / BPM)
    # NOTA: Ajusta los nombres de las columnas ('BPM', 'Edad', etc.) según correspondan exactamente en tu CSV
    
    def calcular_triaje(row):
        # Asumiendo que existe una columna de frecuencia cardíaca (BPM)
        # Si tu columna se llama diferente, cámbiala aquí
        bpm = row.get('BPM', 70) 
        
        if bpm > 120 or bpm < 45:
            return "🔴 Crítico (Paro/Taquicardia Grave)"
        elif bpm > 100 or bpm < 60:
            return "🟡 Moderado (Monitoreo Requerido)"
        else:
            return "🟢 Estable"

    # Aplicamos la lógica para crear una nueva columna de estado
    if 'BPM' in df.columns:
        df['Estado Triaje'] = df.apply(calcular_triaje, axis=1)
    else:
        # Si no encuentra 'BPM', creamos una clasificación simulada temporal para que la app corra
        df['Estado Triaje'] = ["🟢 Estable"] * len(df)
        st.warning("⚠️ No se detectó la columna 'BPM' en tu archivo. Se asignó 'Estable' por defecto. Revisa los nombres de tus columnas.")

    # 3. Módulos de la Interfaz (Sidebar / Filtros)
    st.sidebar.header("Filtros de Pacientes")
    
    # Filtro por estado de gravedad
    estados_disponibles = df['Estado Triaje'].unique()
    filtro_estado = st.sidebar.multiselect("Gravedad:", estados_disponibles, default=estados_disponibles)
    
    # Filtrar el DataFrame original
    df_filtrado = df[df['Estado Triaje'].isin(filtro_estado)]

    # 4. Indicadores Clave de Rendimiento (KPIs) en la pantalla principal
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Pacientes", len(df_filtrado))
    with col2:
        criticos = len(df_filtrado[df_filtrado['Estado Triaje'].str.contains("🔴")])
        st.metric("🔴 Estado Crítico", criticos)
    with col3:
        moderados = len(df_filtrado[df_filtrado['Estado Triaje'].str.contains("🟡")])
        st.metric("🟡 Estado Moderado", moderados)
    with col4:
        estables = len(df_filtrado[df_filtrado['Estado Triaje'].str.contains("🟢")])
        st.metric("🟢 Estado Estable", estables)

    st.markdown("---")

    # 5. Visualización Gráfica del Dataset
    left_column, right_column = st.columns(2)
    
    with left_column:
        st.subheader("Distribución de Pacientes por Triaje")
        fig_pie = px.pie(df_filtrado, names='Estado Triaje', color='Estado Triaje',
                         color_discrete_map={"🟢 Estable": "green", "🟡 Moderado": "orange", "🔴 Crítico": "red"})
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with right_column:
        st.subheader("Vista Rápida de Datos")
        # Mostramos las columnas esenciales del CSV (puedes filtrar cuáles mostrar)
        st.dataframe(df_filtrado, use_container_width=True)

    # 6. Sección de Reporte Clínico Individual
    st.markdown("---")
    st.subheader("📝 Generador de Reporte Clínico Individual")
    
    # Selector de paciente por ID (asumiendo columna 'ID' o 'Patient_ID')
    col_id = 'ID' if 'ID' in df.columns else df.columns[0]
    paciente_seleccionado = st.selectbox("Selecciona el ID del Paciente para revisar detalles:", df_filtrado[col_id])
    
    datos_paciente = df_filtrado[df_filtrado[col_id] == paciente_seleccionado].iloc[0]
    
    # Mostrar la "Ficha Clínica" resumida del paciente
    st.json(datos_paciente.to_dict())
