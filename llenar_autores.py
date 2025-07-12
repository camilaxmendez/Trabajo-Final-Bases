import streamlit as st
from supabase import create_client, Client
from textblob import TextBlob
import requests

# Supabase config
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
NEWSAPI_KEY = '8a3c1aa5081347b790ffe520bbb21594'

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Obtener fuentes desde la API ===
def obtener_fuentes_newsapi():
    url = 'https://newsapi.org/v2/sources'
    params = {
        'language': 'en',
        'apiKey': NEWSAPI_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("sources", [])
    else:
        print(f"Error al obtener fuentes: {response.status_code}")
        return []

# === Insertar fuente usando la función RPC en Supabase ===
def insertar_fuentes_supabase(fuentes):
    for fuente in fuentes:
        payload = {
            "p_id": fuente.get("id"),
            "p_nombre": fuente.get("name"),
            "p_descripcion": fuente.get("description"),
            "p_url": fuente.get("url"),
            "p_categoria": fuente.get("category"),
            "p_lenguaje": fuente.get("language"),
            "p_pais": fuente.get("country")
        }
        try:
            result = supabase.rpc("insertar_fuente", payload).execute()
            print(f"✓ Fuente insertada: {fuente.get('name')}")
        except Exception as e:
            print(f"✗ Error insertando fuente {fuente.get('id')}: {e}")

# === Main ===
if __name__ == "__main__":
    fuentes = obtener_fuentes_newsapi()
    if fuentes:
        insertar_fuentes_supabase(fuentes)
    else:
        print("No se encontraron fuentes para insertar.")
