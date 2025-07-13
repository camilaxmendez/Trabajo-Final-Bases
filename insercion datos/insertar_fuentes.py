import requests
from supabase import create_client, Client
from datetime import datetime

# Configuración
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
NEWSAPI_KEY = "8a3c1aa5081347b790ffe520bbb21594"
#NEWSAPI_KEY = "91722c1669c5404db89694176cf8d9c4"

# Crear cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_fuentes():
    """Obtiene fuentes de noticias desde NewsAPI"""
    url = 'https://newsapi.org/v2/top-headlines/sources'
    params = {
        'language': 'en',
        'apiKey': NEWSAPI_KEY
    }
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get('sources', [])
    except Exception as e:
        print(f"✗ Error al obtener fuentes: {e}")
        return []

def procesar_resultado_fuente(resultado, nombre_fuente):
    """Procesa y muestra el resultado de la inserción de una fuente"""
    operacion = resultado.get("operacion", "desconocido")
    mensaje = resultado.get("mensaje", "sin mensaje")
    id_afectado = resultado.get("id_afectado")
    
    if operacion == 'creación':
        print(f"✓ [{nombre_fuente}] Fuente creada (ID: {id_afectado})")
    elif operacion == 'error':
        # Extraer solo el mensaje principal si es un error de duplicado
        if 'duplicada' in mensaje.lower():
            mensaje = mensaje.split(':')[0]
        print(f"✗ [{nombre_fuente}] {mensaje}")
    else:
        print(f"ℹ️ [{nombre_fuente}] {mensaje}")

def insertar_fuentes_en_supabase(fuentes):
    """Inserta fuentes en Supabase y muestra resultados consistentes"""
    total = len(fuentes)
    exitosas = 0
    errores = 0
    
    for idx, fuente in enumerate(fuentes, 1):
        nombre_fuente = fuente.get("name", "Sin nombre")
        print(f"\n[{idx}/{total}] Procesando: {nombre_fuente}")
        
        try:
            response = supabase.rpc("insertar_fuente", {
                "p_id_api": fuente.get("id"),
                "p_nombre": nombre_fuente,
                "p_descripcion": fuente.get("description", ""),
                "p_url": fuente.get("url", ""),
                "p_categoria": fuente.get("category", "general"),
                "p_lenguaje": fuente.get("language", "en"),
                "p_pais": fuente.get("country", "us")
            }).execute()

            # Procesar cada resultado (normalmente solo habrá uno)
            for resultado in response.data:
                procesar_resultado_fuente(resultado, nombre_fuente)
                if resultado.get("operacion") == 'creación':
                    exitosas += 1
                else:
                    errores += 1
                    
        except Exception as e:
            errores += 1
            print(f"✗ [{nombre_fuente}] Error en la llamada a la función: {str(e)}")
    
    # Resumen final
    print(f"\n{'='*40}")
    print("RESUMEN DE IMPORTACIÓN")
    print(f"Fuentes procesadas: {total}")
    print(f"✓ Insertadas correctamente: {exitosas}")
    print(f"✗ Con errores: {errores}")
    print(f"{'='*40}")

def main():
    """Función principal"""
    print("🔍 Obteniendo fuentes desde NewsAPI...")
    fuentes = obtener_fuentes()
    
    if not fuentes:
        print("No se encontraron fuentes para procesar")
        return
    
    print(f"\n📦 {len(fuentes)} fuentes encontradas. Iniciando importación...")
    insertar_fuentes_en_supabase(fuentes)

if __name__ == "__main__":
    main()