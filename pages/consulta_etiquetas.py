import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Consulta etiquetas")

limite = st.slider("Cantidad de etiquetas a mostrar", min_value=5, max_value=30, value=10)

if st.button("Mostrar Top Etiquetas"):
    response = supabase.rpc('obtener_top_etiquetas', {'p_limite': limite}).execute()

    if response.data:
        df = pd.DataFrame(response.data)
        fig = px.bar(
            df,
            x='total_usos',
            y='etiqueta',
            orientation='h',
            title="Top Etiquetas Más Usadas",
            text='total_usos'
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos de etiquetas.")