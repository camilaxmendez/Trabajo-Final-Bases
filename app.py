import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Credenciales de Supabase
url = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"

NEWSAPI_KEY = '8a3c1aa5081347b790ffe520bbb21594'


CATEGORIAS = [
    "business", "entertainment", "general", "health", "science", "sports", "technology"
]

# --- Función: obtener noticias por categoría ---
def obtener_noticias_por_categoria(categoria):
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'category': categoria,
        'language': 'es',
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

# --- Función principal de inserción ---
def insertar_noticia_completa(conn, noticia, categoria):
    with conn.cursor() as cur:
        # Extraer campos
        titulo = noticia.get("title")
        descripcion = noticia.get("description")
        url = noticia.get("url")
        url_imagen = noticia.get("urlToImage")
        fecha = noticia.get("publishedAt")
        contenido = noticia.get("content")
        fuente_nombre = noticia.get("source", {}).get("name")
        autores_str = noticia.get("author")  # Puede venir "Juan Pérez, María López"
        etiquetas = categoria  # Usamos categoría como etiqueta

        # Buscar ID de la fuente por nombre
        cur.execute("SELECT id FROM fuentes WHERE nombre = %s", (fuente_nombre,))
        fuente = cur.fetchone()
        if not fuente:
            print(f"Fuente '{fuente_nombre}' no encontrada, se ignora noticia.")
            return
        fuente_id = fuente[0]

        # Insertar noticia y obtener ID
        cur.execute("""
            SELECT insertar_noticia(
                %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            titulo, descripcion, categoria, url, url_imagen,
            fecha, contenido, fuente_id
        ))
        noticia_id = cur.fetchone()[0]

        if not noticia_id:
            print(f"✗ Noticia ya existente: {titulo}")
            return

        # Insertar autores
        if autores_str:
            autores = [a.strip() for a in autores_str.split(',') if a.strip()]
            for autor in autores:
                cur.execute("SELECT insertar_autor(%s)", (autor,))
                autor_id = cur.fetchone()[0]
                cur.execute("SELECT asociar_noticia_autor(%s, %s)", (noticia_id, autor_id))

        # Insertar etiqueta como nombre de categoría
        cur.execute("SELECT insertar_etiqueta(%s)", (etiquetas,))
        etiqueta_id = cur.fetchone()[0]
        cur.execute("SELECT asociar_noticia_etiqueta(%s, %s)", (noticia_id, etiqueta_id))

        # Sentimiento del título
        if titulo:
            nombre_sent, puntuacion = analizar_sentimiento(titulo)
            cur.execute("""
                SELECT insertar_sentimiento(%s, %s, %s)
            """, (noticia_id, nombre_sent, puntuacion))


# --- Proceso general ---
def main():
    supabase: Client = create_client(url, key)

    st.title("Noticias desde Supabase")

    # Leer datos de la tabla
    response = supabase.table("noticias").select("*").execute()
    data = response.data

    df = pd.DataFrame(data)
    st.dataframe(df)
    for categoria in CATEGORIAS:
        noticias = obtener_noticias_por_categoria(categoria)
        for noticia in noticias:
            try:
                insertar_noticia_completa(conn, noticia, categoria)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"✗ Error procesando noticia: {e}")
    conn.close()

# --- Ejecutar ---
main()