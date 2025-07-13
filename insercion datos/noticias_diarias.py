from supabase import create_client, Client
import requests
from itertools import islice
from datetime import datetime
from textblob import TextBlob

# Configuración
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
NEWSAPI_KEY = "8a3c1aa5081347b790ffe520bbb21594"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def obtener_fuentes_con_id_api():
    try:
        # Llamar a la función PostgreSQL que creamos
        response = supabase.rpc('obtener_fuentes_con_id_api').execute()
        
        # Verificar si hay errores
        if hasattr(response, 'error') and response.error:
            print(f"Error al obtener fuentes: {response.error}")
            return []
            
        # Extraer solo los id_api de las fuentes que lo tienen
        return [item['id_api'] for item in response.data if item.get('id_api')]
        
    except Exception as e:
        print(f"Excepción al obtener fuentes: {str(e)}")
        return []

def dividir_en_lotes(lista, tamaño):
    it = iter(lista)
    return iter(lambda: list(islice(it, tamaño)), [])

# === 2. Llamar a NewsAPI ===
def consumir_newsapi_por_fuente_lote(fuentes_lote):
    joined_sources = ",".join(fuentes_lote)
    print(f"-----Fuentes: {joined_sources}\n")
    url = "https://newsapi.org/v2/everything"
    params = {
        "apiKey": NEWSAPI_KEY,
        "sources": joined_sources,
        "pageSize": 100
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error al llamar a NewsAPI: {response.status_code} - {response.text}")
        return []
    return response.json().get("articles", [])

def analizar_sentimiento(texto):
    blob = TextBlob(texto or "")
    polaridad = blob.sentiment.polarity
    if polaridad > 0.1:
        return 'positivo', round(polaridad, 3)
    elif polaridad < -0.1:
        return 'negativo', round(polaridad, 3)
    else:
        return 'neutral', round(polaridad, 3)

def insertar_noticia(article):
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

        # Llamar a la función PostgreSQL que devuelve una tabla
        response = supabase.rpc("insertar_noticia_completa", {
            "p_titulo": titulo,
            "p_descripcion": descripcion,
            "p_categoria": "general",
            "p_url": url,
            "p_url_imagen": url_imagen,
            "p_fecha_publicacion": fecha,
            "p_contenido": contenido,
            "p_fuente_nombre": fuente_nombre,
            "p_fuente_id_api": fuente_id_api,
            "p_autores": autores,
            "p_etiquetas": [],
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

# === 4. Ejecutar todo ===
def main():
    fuentes = obtener_fuentes_con_id_api()
    lotes = dividir_en_lotes(fuentes, 20)

    for i, lote in enumerate(lotes):
        print(f"\n🔎 Lote {i+1} ({len(lote)} fuentes): {', '.join(lote)}")
        articulos = consumir_newsapi_por_fuente_lote(lote)
        print(f"📰 Artículos recibidos: {len(articulos)}")

        for articulo in articulos:
            insertar_noticia(articulo)

if __name__ == "__main__":
    main()
