import requests
from supabase import create_client, Client

# === Configuración Supabase ===
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
NEWSAPI_KEY = "91722c1669c5404db89694176cf8d9c4"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Configuración NewsAPI ===

# === Obtener noticias ===
def obtener_noticias():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "language": "en",
        "pageSize": 10,
        "apiKey": NEWSAPI_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("exito")
        return response.json().get("articles", [])
    else:
        print("✗ Error al obtener noticias:", response.status_code)
        return []

# === Insertar título usando RPC ===
def insertar_titulo(titulo):
    try:
        supabase.rpc("insertar_titulo_noticia", {"p_titulo": titulo}).execute()
        print(f"✓ Título insertado: {titulo}")
    except Exception as e:
        print(f"✗ Error insertando título: {e}")

# === MAIN ===
if __name__ == "__main__":
    noticias = obtener_noticias()
    print(noticias)
    for noticia in noticias:
        titulo = noticia.get("title")
        if titulo:
            insertar_titulo(titulo)
