import streamlit as st
import pandas as pd
from supabase import create_client, Client
from forms.fuentes_editar import editar_fuente_form
from forms.fuentes_info import info_fuentes_form

# === Conexión Supabase ===
SUPABASE_URL = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

@st.dialog("Editar fuente")
def editar_fuente(id_fuente):
    fuente = obtener_fuente_por_id(id_fuente)
    editar_fuente_form(fuente)

@st.dialog("Detalles fuente")
def ver_fuente(id_fuente):
    fuente = obtener_fuente_por_id(id_fuente)
    info_fuentes_form(fuente)

def obtener_fuentes_activas() -> dict:
    try:
        # Ejecutar la función PostgreSQL
        response = supabase.rpc(
            'obtener_fuentes_activas'
        ).execute()
        
        fuentes = response.data
        
        # Convertir a DataFrame
        df = pd.DataFrame(fuentes) if fuentes else pd.DataFrame()
        
        # Manejar casos donde no haya nombre de fuente
        if 'fuente_nombre' in df.columns:
            df['fuente_nombre'] = df['fuente_nombre'].fillna('Desconocida')
        else:
            df['fuente_nombre'] = 'Fuente no disponible'
            
        return df
            
    except Exception as e:
        st.error(f"Error al obtener fuentes: {e}")
        return None

df = obtener_fuentes_activas()

def obtener_fuente_por_id(fuente_id: int) -> dict:
    if not isinstance(fuente_id, int) or fuente_id <= 0:
        st.warning("ID de fuente inválido")
        return None

    try:
        with st.spinner(f"Buscando fuente ID {fuente_id}..."):
            response = supabase.rpc(
                'obtener_fuente_por_id',
                {'p_id_fuente': fuente_id}
            ).execute()

            if not response.data:
                st.warning(f"Fuente con ID {fuente_id} no encontrada")
                return None
                
            fuente = response.data[0]
            
            # Verificar si está eliminada
            if fuente.get('eliminado'):
                st.warning(f"⚠️ La fuente '{fuente['nombre']}' está marcada como eliminada")
            
            return fuente

    except Exception as e:
        error_msg = str(e)
        if "fuente" in error_msg.lower() and "no existe" in error_msg.lower():
            st.error(f"La fuente ID {fuente_id} no existe en la base de datos")
        else:
            st.error(f"Error de conexión con la base de datos: {error_msg}")
        return None

def eliminar_fuente(id_fuente: int, eliminar: bool = True) -> bool:
    try:
        # Llamar a la función PostgreSQL a través de Supabase
        response = supabase.rpc(
            'eliminar_fuente',
            {
                'fuente_id': id_fuente,
                'eliminar': eliminar
            }
        ).execute()
        
    except Exception as e:
        st.error(f"❌ Error al {'eliminar' if eliminar else 'recuperar'} la fuente: {str(e)}")
        return False


# === Tabla de noticias principal ===
st.title("📰 Tabla de Fuentes")
st.markdown("### 📋 Fuentes registradas")

# Configuración de paginación
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

if df.empty:
    st.warning("No hay fuentes registradas.")
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
    
    st.caption(f"Página {st.session_state.current_page + 1} de {total_pages} | Total fuentes: {len(df)}")
    
    # Obtener los datos para la página actual
    start_idx = st.session_state.current_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(df))
    current_page_data = df.iloc[start_idx:end_idx]
    
    # Mostrar encabezados
    headers = st.columns(9)
    headers[0].markdown("**ID**")
    headers[1].markdown("**ID API**")
    headers[2].markdown("**Nombre**")
    headers[3].markdown("**Descripción**")
    headers[4].markdown("**URL**")
    headers[5].markdown("**Categoría**")
    headers[6].markdown("**Lenguaje**")
    headers[7].markdown("**País**")
    headers[8].markdown("**Acción**")

    # Mostrar filas de la página actual
    for _, row in current_page_data.iterrows():
        with st.container():
            cols = st.columns(9)
            cols[0].write(row["id"])
            cols[1].write(row["id_api"] or "-")
            cols[2].write(row["nombre"] or "-")
            cols[3].write(row["descripcion"] or "-")
            cols[4].markdown(f"[🔗 Enlace]({row['url']})" if row["url"] else "-")
            cols[5].write(row["categoria"] or "-")
            cols[6].write(row["lenguaje"] or "-")
            cols[7].write(row["pais"] or "-")
            
            # Acciones como enlaces
            with cols[8]:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button("👁️",key=f"ver_{row}",on_click=ver_fuente, kwargs={"id_fuente": row["id"]})
                with col2:
                    st.button("✏️",key=f"editar_{row}",on_click=editar_fuente, kwargs={"id_fuente": row["id"]})
                with col3:
                    st.button("🗑️",key=f"eliminar_{row}",on_click=eliminar_fuente, kwargs={"id_fuente": row["id"]})

                
                
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