import streamlit as st
from supabase import create_client, Client
from textblob import TextBlob
import requests

# Supabase config
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
NEWSAPI_KEY = "91722c1669c5404db89694176cf8d9c4"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CATEGORIAS = [
    "business", "entertainment", "general", "health", "science", "sports", "technology"
]

# --- Función: obtener noticias por categoría ---
def obtener_noticias_por_categoria(categoria):
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'category': categoria,
        'language': 'en',
        'pageSize': 20,
        'apiKey': NEWSAPI_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        print(f"Error al obtener noticias: {response.status_code}")
        return []

# --- Función: analizar sentimiento del título ---
def analizar_sentimiento(texto):
    blob = TextBlob(texto)
    polaridad = blob.sentiment.polarity
    if polaridad > 0.1:
        sentimiento = 'positivo'
    elif polaridad < -0.1:
        sentimiento = 'negativo'
    else:
        sentimiento = 'neutral'
    return sentimiento, polaridad

# --- Función principal usando supabase.rpc ---
def insertar_noticia_completa(supabase: Client, noticia, categoria):
    titulo = noticia.get("title")
    descripcion = noticia.get("description")
    url = noticia.get("url")
    url_imagen = noticia.get("urlToImage")
    fecha = noticia.get("publishedAt")
    contenido = noticia.get("content")
    fuente_nombre = noticia.get("source", {}).get("name")
    autores_str = noticia.get("author")  # Puede venir "Juan Pérez, María López"
    etiquetas = categoria

    # Buscar ID de la fuente por nombre
    try:
        fuente_result = supabase.table("fuentes").select("id").eq("nombre", fuente_nombre).limit(1).execute()
        if not fuente_result.data:
            print(f"Fuente '{fuente_nombre}' no encontrada, se ignora noticia.")
            return
        fuente_id = fuente_result.data[0]["id"]
    except Exception as e:
        print(f"✗ Error buscando fuente: {e}")
        return

    # Insertar noticia con RPC
    try:
        res = supabase.rpc("insertar_noticia", {
            "p_titulo": titulo,
            "p_descripcion": descripcion,
            "p_categoria": categoria,
            "p_url": url,
            "p_url_imagen": url_imagen,
            "p_fecha_publicacion": fecha,
            "p_contenido": contenido,
            "p_fuente_id": fuente_id
        }).execute()

        if res.data is None:
            print(f"✗ Noticia ya existente: {titulo}")
            return

        noticia_id = res.data
        print(f"✓ Noticia insertada: {titulo}")

    except Exception as e:
        print(f"✗ Error insertando noticia: {e}")
        return

    # Insertar autores
    if autores_str:
        autores = [a.strip() for a in autores_str.split(',') if a.strip()]
        for autor in autores:
            try:
                autor_result = supabase.rpc("insertar_autor", {"p_nombre": autor}).execute()
                autor_id = autor_result.data
                supabase.rpc("asociar_noticia_autor", {
                    "p_id_noticia": noticia_id,
                    "p_id_autor": autor_id
                }).execute()
            except Exception as e:
                print(f"✗ Error insertando/relacionando autor '{autor}': {e}")

    # Insertar etiqueta
    try:
        etiqueta_result = supabase.rpc("insertar_etiqueta", {"p_nombre": etiquetas}).execute()
        etiqueta_id = etiqueta_result.data
        supabase.rpc("asociar_noticia_etiqueta", {
            "p_id_noticia": noticia_id,
            "p_id_etiqueta": etiqueta_id
        }).execute()
    except Exception as e:
        print(f"✗ Error insertando/relacionando etiqueta: {e}")

    # Insertar sentimiento
    if titulo:
        try:
            nombre_sent, puntuacion = analizar_sentimiento(titulo)
            supabase.rpc("insertar_sentimiento", {
                "p_id_noticia": noticia_id,
                "p_nombre": nombre_sent,
                "p_puntuacion": puntuacion
            }).execute()
        except Exception as e:
            print(f"✗ Error insertando sentimiento: {e}")

for categoria in CATEGORIAS:
    print(f"🔍 Procesando categoría: {categoria}")
    noticias = obtener_noticias_por_categoria(categoria)
    for noticia in noticias:
        try:
            insertar_noticia_completa(supabase, noticia, categoria)
        except Exception as e:
            print(f"✗ Error insertando noticia: {e}")