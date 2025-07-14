import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, timedelta
# Conexión a Supabase
# === Conexión Supabase ===
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


st.title("Analisis de sentimientos")

response = supabase.rpc('obtener_distribucion_noticias_fuente_pais').execute()

if response.data:
    df = pd.DataFrame(response.data)
    df['pais'] = df['pais'].fillna('Desconocido')

    fig = px.treemap(
        df,
        path=['pais', 'fuente'],
        values='total_noticias',
        color='porcentaje_total',
        color_continuous_scale='Blues',
        title="Distribución de Noticias por País y Fuente (Treemap)"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No se encontraron datos o hubo un error al consultar.")


# Selección de fechas
col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("Fecha Inicio", datetime.now() - timedelta(days=7))
with col2:
    fecha_fin = st.date_input("Fecha Fin", datetime.now())

# Consulta cuando se hace clic
if st.button("Consultar"):
    response = supabase.rpc('obtener_top_fuentes_por_periodo', {
        'p_fecha_inicio': fecha_inicio.isoformat(),
        'p_fecha_fin': fecha_fin.isoformat()
    }).execute()

    if response.data:
        df = pd.DataFrame(response.data)
        fig = px.bar(
            df,
            x='fuente',
            y='total_noticias',
            title=f"Top 10 Fuentes del {fecha_inicio} al {fecha_fin}",
            text='total_noticias'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No se encontraron datos para ese periodo.")


# Selección de etiquetas
etiquetas_input = st.text_input("Ingrese etiquetas separadas por coma (ej: economy,politics,climate)")

if st.button("Consultar Heatmap") and etiquetas_input:
    etiquetas = [e.strip() for e in etiquetas_input.split(",") if e.strip()]

    response = supabase.rpc('obtener_heatmap_temas_por_fuente', {
        'p_etiquetas': etiquetas
    }).execute()

    if response.data:
        df = pd.DataFrame(response.data)
        heatmap_data = df.pivot(index='etiqueta', columns='fuente', values='total_noticias').fillna(0)

        fig = px.imshow(
            heatmap_data,
            text_auto=True,
            color_continuous_scale='Blues',
            title="Cobertura de Temas por Fuente"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No se encontraron datos para las etiquetas seleccionadas.")