import streamlit as st
import pandas as pd
from supabase import create_client, Client
from forms.noticias_editar import editar_noticias_form
from forms.noticias_info import info_noticias_form

# === Conexión Supabase ===
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

@st.dialog("Editar noticia")
def editar_noticia(id_noticia):
    noticia = obtener_noticia_por_id(id_noticia)
    editar_noticias_form(noticia)

@st.dialog("Detalles noticia")
def ver_noticia(id_noticia):
    noticia = obtener_noticia_por_id(id_noticia)
    info_noticias_form(noticia)

# === Obtener noticias y fuentes ===
def obtener_noticias_con_fuentes():
    try:
        # Ejecutar la función PostgreSQL que ya incluye el join con fuentes
        response = supabase.rpc('obtener_noticias_con_fuentes').execute()
        noticias = response.data
        
        # Convertir a DataFrame
        df = pd.DataFrame(noticias) if noticias else pd.DataFrame()
        
        # Manejar casos donde no haya nombre de fuente
        if 'fuente_nombre' in df.columns:
            df['fuente_nombre'] = df['fuente_nombre'].fillna('Desconocida')
        else:
            df['fuente_nombre'] = 'Fuente no disponible'
            
        return df
        
    except Exception as e:
        print(f"Error al obtener noticias: {e}")
        return pd.DataFrame()

df = obtener_noticias_con_fuentes()

def obtener_noticia_por_id(id_noticia: int) -> dict:
    try:
        # Ejecutar la función PostgreSQL
        response = supabase.rpc(
            'obtener_noticia_por_id',
            {'p_id_noticia': id_noticia}
        ).execute()
        
        # Verificar si se encontraron resultados
        if response.data and len(response.data) > 0:
            return response.data[0]  # Retorna el primer resultado (debería ser único)
        else:
            return None
            
    except Exception as e:
        st.error(f"Error al obtener noticia: {e}")
        return None

def eliminar_noticia(id_noticia: int, eliminar: bool = True) -> bool:
    try:
        # Llamar a la función PostgreSQL a través de Supabase
        response = supabase.rpc(
            'eliminar_noticia',
            {
                'noticia_id': id_noticia,
                'eliminar': eliminar
            }
        ).execute()
        
    except Exception as e:
        st.error(f"❌ Error al {'eliminar' if eliminar else 'recuperar'} la noticia: {str(e)}")
        return False

# === Tabla de noticias principal ===
st.title("📰 Tabla de Noticias")
st.markdown("### 📋 Noticias registradas")

# Configuración de paginación
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

if df.empty:
    st.warning("No hay noticias registradas.")
else:
    # Definir número de elementos por página
    items_per_page = 20
    total_pages = (len(df) - 1) // items_per_page + 1
    
    # Controles de paginación (arriba de la tabla)
    col1, col2, col3, _ = st.columns([1, 1, 1, 5])
    
    with col1:
        if st.button("⏮️ Primera") and st.session_state.current_page > 0:
            st.session_state.current_page = 0
    with col2:
        if st.button("◀️ Anterior") and st.session_state.current_page > 0:
            st.session_state.current_page -= 1
    with col3:
        if st.button("▶️ Siguiente") and st.session_state.current_page < total_pages - 1:
            st.session_state.current_page += 1
    
    st.caption(f"Página {st.session_state.current_page + 1} de {total_pages} | Total noticias: {len(df)}")
    
    # Obtener los datos para la página actual
    start_idx = st.session_state.current_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(df))
    current_page_data = df.iloc[start_idx:end_idx]
    
    # Mostrar encabezados
    headers = st.columns([1, 2, 1, 1, 1, 1, 2])
    headers[0].markdown("**ID**")
    headers[1].markdown("**Título**")
    headers[2].markdown("**Categoría**")
    headers[3].markdown("**URL**")
    headers[4].markdown("**Fecha**")
    headers[5].markdown("**Fuente**")
    headers[6].markdown("**Acciones**")
    
    # Mostrar filas de la página actual
    for _, row in current_page_data.iterrows():
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
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button("👁️",key=f"ver_{row}",on_click=ver_noticia, kwargs={"id_noticia": row["id"]})
                with col2:
                    st.button("✏️",key=f"editar_{row}",on_click=editar_noticia, kwargs={"id_noticia": row["id"]})
                with col3:
                    st.button("🗑️",key=f"eliminar_{row}",on_click=eliminar_noticia, kwargs={"id_noticia": row["id"]})

                #col1, col2, col3, col4 = st.columns(4)
                #with col1:
                #    st.button("👁️",key=f"ver_{row}",on_click=ver_noticia, kwargs={"id_noticia": row["id"]})
                #with col2:
                #    st.button("✏️",key=f"editar_{row}",on_click=editar_noticia, kwargs={"id_noticia": row["id"]})

                #with col3:
                #    st.button("🏷️",key=f"etiqueta_{row}")

                #with col4:
                #    st.button("🗑️",key=f"eliminar_{row}",on_click=eliminar_noticia, kwargs={"id_noticia": row["id"]})

                
                
    # Controles de paginación (debajo de la tabla)
    col1, col2, col3, _ = st.columns([1, 1, 1, 5])
    
    with col1:
        if st.button("⏮️ Primera", key="bottom_first") and st.session_state.current_page > 0:
            st.session_state.current_page = 0
    with col2:
        if st.button("◀️ Anterior", key="bottom_prev") and st.session_state.current_page > 0:
            st.session_state.current_page -= 1
    with col3:
        if st.button("▶️ Siguiente", key="bottom_next") and st.session_state.current_page < total_pages - 1:
            st.session_state.current_page += 1