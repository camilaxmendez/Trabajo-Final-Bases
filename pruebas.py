import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date
import re

# === Conexión Supabase ===
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")
params = st.query_params

# === Obtener noticias y fuentes ===
def obtener_noticias():
    noticias = supabase.table("noticias").select("*").order("fecha_publicacion", desc=True).execute().data
    fuentes = supabase.table("fuentes").select("id, nombre").execute().data
    df_noticias = pd.DataFrame(noticias)
    df_fuentes = pd.DataFrame(fuentes)

    if not df_noticias.empty and not df_fuentes.empty:
        df = df_noticias.merge(df_fuentes, left_on="fuente_id", right_on="id", suffixes=("", "_fuente"))
        df["fuente_nombre"] = df["nombre"]
    else:
        df = df_noticias
        df["fuente_nombre"] = df["fuente_id"]
    return df

df = obtener_noticias()

# === Acciones vía URL ===
if "accion" in params and "id" in params:
    id_noticia = int(params["id"])
    accion = params["accion"]
    noticia = df[df["id"] == id_noticia].iloc[0]

    st.markdown("### 🧭 Navegación de acción")

    if accion == "ver":
        st.subheader(f"🔎 Detalles noticia ID {id_noticia}")
        st.write("**Título:**", noticia["titulo"])
        st.write("**Descripción:**", noticia["descripcion"])
        st.write("**Contenido completo:**", noticia["contenido"] or "—")
        st.write("**Categoría:**", noticia["categoria"])
        st.write("**Fecha publicación:**", noticia["fecha_publicacion"])
        st.write("**Fuente:**", noticia["fuente_nombre"])
        if noticia["url_imagen"]:
            st.image(noticia["url_imagen"])
        st.markdown(f"[🔗 Enlace original]({noticia['url']})")

    elif accion == "edit":
        st.subheader(f"✏️ Editar Noticia ID {id_noticia}")
        noticia = supabase.table("noticias").select("*").eq("id", id_noticia).execute().data
        if not noticia:
            st.error("❌ Noticia no encontrada.")
        else:
            noticia = noticia[0]

            # === Cargar fuentes ===
            fuentes = supabase.table("fuentes").select("id, nombre").execute().data
            opciones_fuentes = {f["nombre"]: f["id"] for f in fuentes}
            fuente_actual = next((k for k, v in opciones_fuentes.items() if v == noticia["fuente_id"]), list(opciones_fuentes.keys())[0])

            categorias_validas = [
                "business", "entertainment", "general", "health", "science", "sports", "technology"
            ]
            cat_idx = categorias_validas.index(noticia["categoria"]) if noticia["categoria"] in categorias_validas else 0

            with st.form(key=f"form_edit_{id_noticia}"):
                nuevo_titulo = st.text_input("📰 Título", value=noticia["titulo"] or "")
                nueva_desc = st.text_area("📝 Descripción", value=noticia["descripcion"] or "")
                nueva_categoria = st.selectbox("📂 Categoría", options=categorias_validas, index=cat_idx)
                nueva_url = st.text_input("🔗 URL", value=noticia["url"] or "")
                nueva_imagen = st.text_input("🖼️ URL Imagen", value=noticia["url_imagen"] or "")
                nueva_fecha = st.date_input("📅 Fecha publicación", value=datetime.fromisoformat(noticia["fecha_publicacion"]).date())
                nuevo_contenido = st.text_area("📄 Contenido", value=noticia["contenido"] or "")
                nueva_fuente_nombre = st.selectbox("🏢 Fuente", options=list(opciones_fuentes.keys()), index=list(opciones_fuentes.keys()).index(fuente_actual))

                submitted = st.form_submit_button("💾 Guardar cambios")
            if submitted:
                errores = []

                # === Validaciones ===
                if len(nuevo_titulo.strip()) < 10:
                    errores.append("El título debe tener al menos 10 caracteres.")
                if len(nueva_desc.strip()) < 10:
                    errores.append("La descripción debe tener al menos 10 caracteres.")
                if "prueba" in nuevo_titulo.lower() or "prueba" in nuevo_contenido.lower():
                    errores.append("El contenido no puede contener la palabra 'prueba'.")
                if not nueva_url.strip():
                    errores.append("La URL no puede estar vacía.")
                elif not re.match(r"^https?://", nueva_url.strip()):
                    errores.append("La URL debe comenzar con http o https.")
                if not nueva_imagen.strip():
                    errores.append("La URL de imagen no puede estar vacía.")
                elif not re.match(r"^https?://", nueva_imagen.strip()):
                    errores.append("La URL de imagen debe comenzar con http o https.")
                if nueva_fecha > datetime.today().date():
                    errores.append("La fecha no puede estar en el futuro.")

                # Evitar duplicados
                otras = df[(df["id"] != id_noticia) & ((df["titulo"] == nuevo_titulo) | (df["url"] == nueva_url))]
                if not otras.empty:
                    errores.append("Ya existe una noticia con ese título o URL.")

                # Validación de cambios reales
                cambios = {
                    "titulo": nuevo_titulo != noticia["titulo"],
                    "descripcion": nueva_desc != noticia["descripcion"],
                    "categoria": nueva_categoria != noticia["categoria"],
                    "url": nueva_url != noticia["url"],
                    "url_imagen": nueva_imagen != noticia["url_imagen"],
                    "fecha_publicacion": nueva_fecha.isoformat() != noticia["fecha_publicacion"][:10],
                    "contenido": nuevo_contenido != (noticia["contenido"] or ""),
                    "fuente_id": opciones_fuentes[nueva_fuente_nombre] != noticia["fuente_id"]
                }

                if not any(cambios.values()):
                    errores.append("No se detectaron cambios en los datos.")

                if errores:
                    for err in errores:
                        st.error(err)
                else:
                    supabase.table("noticias").update({
                        "titulo": nuevo_titulo,
                        "descripcion": nueva_desc,
                        "categoria": nueva_categoria,
                        "url": nueva_url,
                        "url_imagen": nueva_imagen,
                        "fecha_publicacion": nueva_fecha.isoformat(),
                        "contenido": nuevo_contenido,
                        "fuente_id": opciones_fuentes[nueva_fuente_nombre]
                    }).eq("id", id_noticia).execute()

                    st.success("✅ Cambios guardados correctamente.")
                    st.experimental_set_query_params()
                    st.rerun()

    elif accion == "tag":
        st.subheader(f"🏷️ Etiquetado pendiente para ID {id_noticia}")
        st.info("Aquí iría el etiquetado")

    elif accion == "del":
        st.subheader(f"🗑️ Confirmar eliminación de Noticia ID {id_noticia}")

        st.warning("⚠️ Esta acción eliminará la noticia, sus etiquetas, autores y sentimientos asociados. ¿Estás segura?")

        col_conf1, col_conf2 = st.columns(2)
        if col_conf1.button("✅ Sí, eliminar permanentemente"):
            # Eliminar asociaciones primero (si no tienes ON DELETE CASCADE)
            supabase.table("noticias_etiquetas").delete().eq("id_noticia", id_noticia).execute()
            supabase.table("noticias_autores").delete().eq("id_noticia", id_noticia).execute()
            supabase.table("sentimientos").delete().eq("id_noticia", id_noticia).execute()

            # Luego eliminar la noticia
            supabase.table("noticias").delete().eq("id", id_noticia).execute()
            st.success(f"✅ Noticia ID {id_noticia} eliminada correctamente.")
            st.experimental_set_query_params()
            st.rerun()

        if col_conf2.button("❌ Cancelar"):
            st.experimental_set_query_params()
            st.rerun()

    if st.button("🔙 Volver"):
        st.experimental_set_query_params()
        st.rerun()

    st.stop()

# === Tabla de noticias principal ===
st.title("📰 Tabla de Noticias")
st.markdown("### 📋 Noticias registradas")

if df.empty:
    st.warning("No hay noticias registradas.")
else:
    headers = st.columns([1, 2, 1, 1, 1, 1, 2])
    headers[0].markdown("**ID**")
    headers[1].markdown("**Título**")
    headers[2].markdown("**Categoría**")
    headers[3].markdown("**URL**")
    headers[4].markdown("**Fecha**")
    headers[5].markdown("**Fuente**")
    headers[6].markdown("**Acciones**")

    for _, row in df.iterrows():
        with st.container():
            cols = st.columns([1, 2, 1, 1, 1, 1, 2])
            cols[0].write(row["id"])
            cols[1].write(row["titulo"] or "-")
            cols[2].write(row["categoria"] or "-")
            cols[3].markdown(f"[🔗 Enlace]({row['url']})" if row["url"] else "-")
            cols[4].write(row["fecha_publicacion"][:19] if row["fecha_publicacion"] else "-")
            cols[5].write(row["fuente_nombre"] or "-")

            # Acciones como enlaces
            with cols[6]:
                st.markdown(
                    f"""
                    <a href="?accion=ver&id={row['id']}"><button>👁️</button></a>
                    <a href="?accion=edit&id={row['id']}"><button>✏️</button></a>
                    <a href="?accion=tag&id={row['id']}"><button>🏷️</button></a>
                    <a href="?accion=del&id={row['id']}"><button style='color:red;'>🗑️</button></a>
                    """,
                    unsafe_allow_html=True
                )
