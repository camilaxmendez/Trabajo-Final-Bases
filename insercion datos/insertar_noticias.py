import requests
from textblob import TextBlob
from supabase import create_client, Client, SupabaseException
from datetime import datetime
from keybert import KeyBERT
from difflib import get_close_matches

# Configuración
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
NEWSAPI_KEY = "8a3c1aa5081347b790ffe520bbb21594"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

#CATEGORIAS = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
CATEGORIAS = ['business', 'entertainment', 'general', 'health', 'science', 'technology']

LANG = 'en'

def analizar_sentimiento(texto):
    blob = TextBlob(texto or "")
    polaridad = blob.sentiment.polarity
    if polaridad > 0.1:
        return 'positivo', round(polaridad, 3)
    elif polaridad < -0.1:
        return 'negativo', round(polaridad, 3)
    else:
        return 'neutral', round(polaridad, 3)

def extraer_etiquetas(texto, min_score=0.2, top_n=5, similitud_min=0.85):
    kw_model = KeyBERT()
    resultados = kw_model.extract_keywords(
        texto,
        keyphrase_ngram_range=(1, 1),
        stop_words='english',
        top_n=top_n * 2  # Obtener más para luego filtrar
    )
    
    # Filtrar por score y normalizar
    etiquetas = [kw.lower() for kw, score in resultados if score >= min_score]

    # Eliminar duplicados exactos
    unicas = list(set(etiquetas))

    # Filtrar por similitud para evitar términos casi iguales
    final = []
    for etiqueta in unicas:
        if not get_close_matches(etiqueta, final, cutoff=similitud_min):
            final.append(etiqueta)

    # Limitar al top_n final
    return final[:top_n]


def obtener_noticias(categoria):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": NEWSAPI_KEY,
        "category": categoria,
        "language": LANG
    }
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("articles", [])
    except Exception as e:
        print(f"⚠️ Error HTTP al obtener noticias de {categoria}: {e}")
        print(f"⚠️ Error HTTP al obtener noticias de {categoria}: {e}")
        return []

def insertar_noticia(article, categoria):
    try:
        titulo = article.get("title")
        descripcion = article.get("description")
        url = article.get("url")
        url_imagen = article.get("urlToImage")
        fecha = article.get("publishedAt")
        contenido = article.get("content")

        fuente = article.get("source", {})
        fuente_nombre = fuente.get("name")
        fuente_id_api = fuente.get("id")

        autores_raw = article.get("author")
        autores = [a.strip() for a in autores_raw.split(",")] if autores_raw else []

        sentimiento, puntuacion = analizar_sentimiento(titulo)

        texto = f"{titulo}. {descripcion}"
        etiquetas = extraer_etiquetas(texto)
        
        # Llamar a la función PostgreSQL que devuelve una tabla
        response = supabase.rpc("insertar_noticia_completa", {
            "p_titulo": titulo,
            "p_descripcion": descripcion,
            "p_categoria": categoria,
            "p_url": url,
            "p_url_imagen": url_imagen,
            "p_fecha_publicacion": fecha,
            "p_contenido": contenido,
            "p_fuente_nombre": fuente_nombre,
            "p_fuente_id_api": fuente_id_api,
            "p_autores": autores,
            "p_etiquetas": etiquetas,
            "p_sentimiento_nombre": sentimiento,
            "p_sentimiento_puntuacion": puntuacion
        }).execute()

        # Procesar los resultados en formato de tabla
        resultados = response.data
        
        if not resultados:
            print(f"✗ No se recibieron resultados para: {titulo[:50]}")
            return
        
        # Mostrar cada fila de resultado
        for resultado in resultados:
            operacion = resultado.get("operacion", "desconocido")
            mensaje = resultado.get("mensaje", "sin mensaje")
            id_afectado = resultado.get("id_afectado")
            tipo_entidad = resultado.get("tipo_entidad", "desconocido")
            
            # Formatear el mensaje según el tipo de operación
            timestamp = datetime.now().strftime("%H:%M:%S")
            prefijo = f"[{timestamp}] [{tipo_entidad.upper()}]"
            
            if operacion == 'error':
                print(f"{prefijo} 🔥 ERROR: {mensaje}")
            elif operacion == 'creación':
                print(f"{prefijo} ✅ CREADO (ID: {id_afectado}): {mensaje}")
            elif operacion == 'existente':
                print(f"{prefijo} 🔄 EXISTENTE (ID: {id_afectado}): {mensaje}")
            elif operacion == 'relación':
                print(f"{prefijo} 🔗 RELACIÓN: {mensaje}")
            elif operacion == 'éxito':
                print(f"{prefijo} 🎉 ÉXITO: {mensaje}")
            else:
                print(f"{prefijo} ℹ️ INFO: {mensaje}")
                
        # Separador visual entre noticias
        print("-" * 80)

    except SupabaseException as e:
        print(f"[ERROR SUPABASE] 🔥 Error en Supabase: {str(e)}")
    except Exception as e:
        print(f"[ERROR GENERAL] ⚠️ Error inesperado: {str(e)}")

def main():
    for categoria in CATEGORIAS:
        print(f"\n🔍 Procesando categoría: {categoria.upper()}")
        noticias = obtener_noticias(categoria)
        print(f"📦 {len(noticias)} noticias encontradas en {categoria}")
        
        for idx, noticia in enumerate(noticias, 1):
            print(f"\n📰 Procesando noticia {idx}/{len(noticias)}")
            insertar_noticia(noticia, categoria)

if __name__ == "__main__":
    main()

    