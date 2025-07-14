import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# === Conexión Supabase ===
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def sentimiento_por_pais(categoria) -> dict:
    try:
        # Ejecutar la función PostgreSQL
        response = supabase.rpc('obtener_sentimiento_por_pais', {'p_categoria': categoria}).execute()
        
        return pd.DataFrame(response.data)
            
    except Exception as e:
        st.error(f"Error al obtener sentimientos por pais: {e}")
        return None


# --- Streamlit App ---
st.title("Análisis de sentimientos")

categorias_validas = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
categoria_seleccionada = st.selectbox("Selecciona una categoría:", categorias_validas)

if categoria_seleccionada:
    df = sentimiento_por_pais(categoria_seleccionada)

    if df.empty:
        st.warning("No se encontraron datos para esta categoría.")
    else:
        # Calcular porcentaje por país
        df_total = df.groupby('pais')['cantidad_noticias'].sum().reset_index().rename(columns={'cantidad_noticias': 'total'})
        df_merged = pd.merge(df, df_total, on='pais')
        df_merged['porcentaje'] = (df_merged['cantidad_noticias'] / df_merged['total'])

        # Crear gráfico apilado
        fig = px.bar(
            df_merged,
            x='pais',
            y='porcentaje',
            color='sentimiento',
            title=f"Distribución de Sentimiento por País para '{categoria_seleccionada}'",
            text_auto='.2f'
        )
        fig.update_layout(barmode='stack', yaxis=dict(tickformat='%'))
        st.plotly_chart(fig, use_container_width=True)

sentimientos_validos = ['positivo', 'neutral', 'negativo']
sentimiento_seleccionado = st.selectbox("Selecciona un sentimiento:", sentimientos_validos)

if sentimiento_seleccionado:
    response = supabase.rpc('obtener_fuentes_por_sentimiento', {'p_sentimiento': sentimiento_seleccionado}).execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        fig = px.bar(
            df,
            x='cantidad',
            y='fuente',
            orientation='h',
            title=f"Medios con más noticias '{sentimiento_seleccionado}'",
            text='cantidad'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No se encontraron datos o hubo un error al consultar.")