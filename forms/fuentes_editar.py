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
    len_idx = lenguajes_validos.index(fuente["lenguaje"]) if fuente["lenguaje"] in lenguajes_validos else 0

    paises_validos = [
        "ae","ar","at","au","be","bg","br","ca","ch","cn","co","cu","cz","de","eg","fr","gb","gr","hk","hu",
        "id","ie","il","in","it","jp","kr","lt","lv","ma","mx","my","ng","nl","no","nz","ph","pl","pt","ro",
        "rs","ru","sa","se","sg","si","sk","th","tr","tw","ua","us","ve","za"
    ]
    pai_idx = paises_validos.index(fuente["pais"]) if fuente["pais"] in paises_validos else 0
    
    with st.form("fuentes_form"):
        nuevo_nombre = st.text_input("📰 Nombre", value=fuente["nombre"] or "")
        nueva_desc = st.text_area("📝 Descripción", value=fuente["descripcion"] or "")
        nueva_url = st.text_input("🔗 URL", value=fuente["url"] or "")
        nueva_categoria = st.selectbox("📂 Categoría", options=categorias_validas, index=cat_idx)
        nuevo_lenguaje = st.selectbox("🗣️ Lenguaje", options=lenguajes_validos, index=len_idx)
        nuevo_pais = st.selectbox("🌍 Pais", options=paises_validos, index=pai_idx)
        nuevo_id_api = st.text_input("📄 ID API", value=fuente["id_api"] or "")
        submitted = st.form_submit_button("💾 Guardar cambios")
        
        if submitted:
            errores = []

            # === Validaciones ===
            if len(nuevo_nombre.strip()) < 0:
                errores.append("Ingrese un nombre válido")
            if len(nueva_desc.strip()) < 0:
                errores.append("Ingrese una descripción válida.")
            if len(nuevo_id_api.strip()) < 0:
                errores.append("Ingrese un id válido.")
            if not nueva_url.strip():
                errores.append("La URL no puede estar vacía.")
            elif not re.match(r"^https?://", nueva_url.strip()):
                errores.append("La URL debe comenzar con http o https.")

            # Validación de cambios reales
            cambios = {
                "nombre": nuevo_nombre != fuente["nombre"],
                "descripcion": nueva_desc != fuente["descripcion"],
                "url": nueva_url != fuente["url"],
                "lenguaje": nuevo_lenguaje != fuente["lenguaje"],
                "pais": nuevo_pais != fuente["pais"],
                "id_api": nuevo_id_api != fuente["id_api"]
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
                        'actualizar_fuente',
                        {
                            'p_id': fuente["id"],
                            'p_nombre': nuevo_nombre,
                            'p_descripcion': nueva_desc,
                            'p_url': nueva_url,
                            'p_categoria': nueva_categoria,
                            'p_lenguaje': nuevo_lenguaje,
                            'p_pais': nuevo_pais,
                            'p_id_api': nuevo_id_api
                        }
                    ).execute()

                    # Procesar la respuesta
                    if response.data:
                        result = response.data[0]  # Tomamos el primer resultado
                        if result['operacion'] == 'error':
                            st.error(f"❌ Error: {result['mensaje']}")
                        else:
                            st.success(f"✅ {result['mensaje']}")
                            #st.experimental_set_query_params()
                            st.rerun()
                    else:
                        st.error("No se recibió respuesta de la base de datos")

                except Exception as e:
                    st.error(f"Error al conectar con la base de datos: {str(e)}")

