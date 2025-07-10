import streamlit as st
import requests
import pandas as pd
from textblob import TextBlob

st.title("Noticias desde Supabase")

# Aquí puedes mostrar noticias simuladas por ahora
df = pd.DataFrame([
    {"Título": "La educación avanza", "Fuente": "BBC", "Fecha": "2025-07-01", "Sentimiento": "positivo"},
    {"Título": "Crisis educativa en zonas rurales", "Fuente": "El Comercio", "Fecha": "2025-07-02", "Sentimiento": "negativo"}
])

st.dataframe(df)

# Simulación de análisis de sentimientos
st.markdown("### Análisis de sentimientos")
st.bar_chart(df['Sentimiento'].value_counts())
