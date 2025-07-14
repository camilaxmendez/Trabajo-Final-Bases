import streamlit as st
from matplotlib import pyplot as plt
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import pycountry
from collections import Counter
import re

# === Conexión Supabase ===
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Dashboard de Noticias", layout="wide")
st.title("🧠 Sistema de Inteligencia Mediática")
st.markdown("Visualización de estadísticas de noticias almacenadas en Supabase.")


# Convertir código de país ISO-2 a ISO-3
def iso2_a_iso3(codigo_iso2):
    try:
        return pycountry.countries.get(alpha_2=codigo_iso2.upper()).alpha_3
    except:
        return None

# === MAPA DE COROPLETAS POR PAÍS ===
res = supabase.rpc("obtener_distribucion_geografica").execute()
res_pais = supabase.rpc("obtener_distribucion_geografica").execute()
df_pais = pd.DataFrame(res_pais.data)
st.dataframe(df_pais, use_container_width=True)

if res.data:
    df_geo = pd.DataFrame(res.data)

    # Asegurarse de que las columnas estén bien nombradas
    df_geo.columns = ["pais", "cantidad"]

    # Convertir ISO2 a ISO3
    df_geo["pais_iso3"] = df_geo["pais"].apply(iso2_a_iso3)

    # Mostrar mapa
    st.subheader("🌍 Cobertura de Noticias por País")
    fig = px.choropleth(
        df_geo,
        locations="pais_iso3",
        color="cantidad",
        hover_name="pais",
        locationmode="ISO-3",
        color_continuous_scale="Blues",
        title="🌍 Distribución Geográfica de Noticias"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No hay datos disponibles para mostrar el mapa.")

# === 1. Noticias por Categoría ===
st.subheader("📚 Noticias por Categoría")

res_categoria = supabase.rpc("obtener_distribucion_noticias_por_categoria").execute()
df_categoria = pd.DataFrame(res_categoria.data)

st.dataframe(df_categoria, use_container_width=True)

fig1 = px.pie(
    df_categoria,
    names="categoria",
    values="cantidad",
    hole=0.5,
    title="Distribución de Noticias por Categoría"
)
st.plotly_chart(fig1, use_container_width=True)


# Obtener todos los títulos desde Supabase
response = supabase.table("noticias").select("titulo").execute()
titulos = [item["titulo"] for item in response.data if item["titulo"]]

# Tokenizar y contar palabras
contador = Counter()
for titulo in titulos:
    palabras = re.findall(r'\b\w+\b', titulo.lower())
    contador.update(palabras)

# Mostrar top 15 palabras
top_palabras = contador.most_common(15)


# --- Noticias por Fuente ---
res_fuente = supabase.rpc("obtener_noticias_por_fuente").execute()
df_fuente = pd.DataFrame(res_fuente.data)
# Mostrar solo las 20 fuentes con más noticias
df_fuente = df_fuente.sort_values("cantidad", ascending=False).head(20)
if not df_fuente.empty:
    st.subheader("📰 Noticias por Fuente")
    st.dataframe(df_fuente)
    fig1, ax1 = plt.subplots()
    ax1.barh(df_fuente["fuente"], df_fuente["cantidad"])
    ax1.set_xlabel("Cantidad")
    st.pyplot(fig1)

# --- Autores más activos ---
res_autores = supabase.rpc("obtener_autores_mas_activos").execute()
df_autores = pd.DataFrame(res_autores.data)
if not df_autores.empty:
    st.subheader("✍️ Top Autores más Activos")
    st.dataframe(df_autores)
    fig2, ax2 = plt.subplots()
    ax2.bar(df_autores["autor"], df_autores["total"])
    ax2.set_xlabel("Autor")
    ax2.set_ylabel("Total de Noticias")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

# --- Palabras clave más frecuentes ---
res_titulos = supabase.table("noticias").select("titulo").execute()
titulos = [item["titulo"] for item in res_titulos.data if item["titulo"]]
contador = Counter()
for titulo in titulos:
    palabras = re.findall(r'\b\w+\b', titulo.lower())
    contador.update(palabras)

top_palabras = contador.most_common(15)
df_palabras = pd.DataFrame(top_palabras, columns=["palabra", "frecuencia"])
st.subheader("🔠 Palabras Clave Más Frecuentes en Títulos")
st.dataframe(df_palabras)
fig3, ax3 = plt.subplots()
ax3.bar(df_palabras["palabra"], df_palabras["frecuencia"])
ax3.set_xlabel("Palabra")
ax3.set_ylabel("Frecuencia")
plt.xticks(rotation=45)
st.pyplot(fig3)