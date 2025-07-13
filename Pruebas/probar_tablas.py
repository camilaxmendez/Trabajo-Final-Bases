from supabase import create_client, Client

# === Configuración de Supabase ===
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Lista de tablas a consultar ===
tablas = [
    "fuentes",
    "noticias",
    "autores",
    "noticias_autores",
    "etiquetas",
    "noticias_etiquetas",
    "sentimientos"
]

# === Ejecutar SELECT * para cada tabla ===
for tabla in tablas:
    try:
        print(f"\n📋 Tabla: {tabla}")
        res = supabase.table(tabla).select("*").limit(10).execute()
        for fila in res.data:
            print(fila)
    except Exception as e:
        print(f"⚠️ Error consultando tabla {tabla}: {e}")