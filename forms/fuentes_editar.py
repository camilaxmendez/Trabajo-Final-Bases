import re
from datetime import datetime, date
import streamlit as st
import requests  # pip install requests
from supabase import create_client, Client

SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_fuentes_activas() -> dict:
    try:
        # Ejecutar la función PostgreSQL
        response = supabase.rpc(
            'obtener_fuentes_activas'
        ).execute()
        
        # Verificar si se encontraron resultados
        if response.data and len(response.data) > 0:
            return response.data  # Retorna el primer resultado (debería ser único)
        else:
            return None
            
    except Exception as e:
        st.error(f"Error al obtener noticia: {e}")
        return None


def editar_fuente_form(fuente):
    categorias_validas = [
        "business", "entertainment", "general", "health", "science", "sports", "technology"
    ]
    cat_idx = categorias_validas.index(fuente["categoria"]) if fuente["categoria"] in categorias_validas else 0
    
    lenguajes_validos = [
        "ar", "de", "en", "es" ,"fr", "he", "it", "nl", "no", "pt", "ru", "sv", "ud", "zh"
    ]
    len_idx = lenguajes_validos.index(fuente["lenguaje"]) if noticia["lenguaje"] in lenguajes_validos else 0

    paises_validos = [
        "ae","ar","at","au","be","bg","br","ca","ch","cn","co","cu","cz","de","eg","fr","gb","gr","hk","hu",
        "id","ie","il","in","it","jp","kr","lt","lv","ma","mx","my","ng","nl","no","nz","ph","pl","pt","ro",
        "rs","ru","sa","se","sg","si","sk","th","tr","tw","ua","us","ve","za"
    ]
    pai_idx = paises_validos.index(fuente["pais"]) if noticia["pais"] in paises_validos else 0
    
    with st.form("noticias_form"):
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
                try:
                    # Llamar a la función de actualización en Supabase
                    response = supabase.rpc(
                        'actualizar_noticia_completa',
                        {
                            'p_noticia_id': noticia["id"],
                            'p_titulo': nuevo_titulo,
                            'p_descripcion': nueva_desc,
                            'p_categoria': nueva_categoria,
                            'p_url': nueva_url,
                            'p_url_imagen': nueva_imagen,
                            'p_fecha_publicacion': nueva_fecha,
                            'p_contenido': nuevo_contenido,
                            'p_fuente_nombre': nueva_fuente_nombre
                        }
                    ).execute()

                    # Procesar la respuesta
                    if response.data:
                        result = response.data[0]  # Tomamos el primer resultado
                        if result['operacion'] == 'error':
                            st.error(f"❌ Error: {result['mensaje']}")
                        else:
                            st.success(f"✅ {result['mensaje']}")
                            st.experimental_set_query_params()
                            st.rerun()
                    else:
                        st.error("No se recibió respuesta de la base de datos")

                except Exception as e:
                    st.error(f"Error al conectar con la base de datos: {str(e)}")
                            

                
                st.success("✅ Cambios guardados correctamente.")
                st.experimental_set_query_params()
                st.rerun()