from supabase import create_client, Client
from datetime import datetime
from datetime import datetime, timezone


# === Configuración de Supabase ===
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === 2. insertar_autor ===
print("📌 insertando autor...")
autor_res = supabase.rpc("insertar_autor", {
    "p_nombre": "Camila Méndez"
}).execute()
autor_id = autor_res.data
print(f"ID autor: {autor_id}")

# === 3. insertar_etiqueta ===
print("📌 insertando etiqueta...")
etiqueta_res = supabase.rpc("insertar_etiqueta", {
    "p_nombre": "tecnología"
}).execute()
etiqueta_id = etiqueta_res.data
print(f"ID etiqueta: {etiqueta_id}")

# === 4. insertar_noticia ===
print("📌 insertando noticia...")
noticia_res = supabase.rpc("insertar_noticia", {
    "p_titulo": "Título de prueba",
    "p_descripcion": "Descripción de la noticia",
    "p_categoria": "general",
    "p_url": "https://noticia.demo",
    "p_url_imagen": "https://noticia.demo/img.jpg",
    "p_fecha_publicacion": datetime.now(timezone.utc).isoformat(),
    "p_contenido": "Contenido de prueba",
    "p_fuente_id": "demo1234"
}).execute()
noticia_id = noticia_res.data
print(f"ID noticia: {noticia_id}")

# === 5. asociar_noticia_autor ===
print("📌 asociando autor a noticia...")
supabase.rpc("asociar_noticia_autor", {
    "p_id_noticia": noticia_id,
    "p_id_autor": autor_id
}).execute()

# === 6. asociar_noticia_etiqueta ===
print("📌 asociando etiqueta a noticia...")
supabase.rpc("asociar_noticia_etiqueta", {
    "p_id_noticia": noticia_id,
    "p_id_etiqueta": etiqueta_id
}).execute()

# === 7. insertar_sentimiento ===
print("📌 insertando sentimiento...")
supabase.rpc("insertar_sentimiento", {
    "p_id_noticia": noticia_id,
    "p_nombre": "positivo",
    "p_puntuacion": 0.9
}).execute()

# === 8. insertar_persona ===
print("📌 insertando persona...")
persona_res = supabase.rpc("insertar_persona", {
    "nombre_persona": "Luis Pérez"
}).execute()
print(f"Persona insertada: {persona_res.data}")

# === 9. insertar_noticia_completa ===
print("📌 insertando noticia completa...")
supabase.rpc("insertar_noticia_completa", {
    "p_titulo": "Noticia Completa desde RPC",
    "p_descripcion": "Una noticia insertada con todos los pasos",
    "p_categoria": "technology",
    "p_url": "https://noticia.rpc/123",
    "p_url_imagen": "https://noticia.rpc/123/img.jpg",
    "p_fecha_publicacion": datetime.now(timezone.utc).isoformat(),
    "p_contenido": "Contenido muy interesante...",

    # Fuente
    "p_fuente_id": "demo123",
    "p_fuente_nombre": "Fuente RPC",
    "p_fuente_descripcion": "Fuente desde RPC",
    "p_fuente_url": "https://fuente.rpc",
    "p_fuente_categoria": "technology",
    "p_fuente_lenguaje": "es",
    "p_fuente_pais": "EC",

    # Autor
    "p_autor": "Ana Guerrero",

    # Etiquetas
    "p_etiquetas": "tecnología,datos,api"
}).execute()
print("🎉 Todo ejecutado con éxito.")
