import re

import streamlit as st
import requests  # pip install requests

def info_noticias_form(noticia):
    with st.form("noticias_info"):
        st.write("**Título:**", noticia["titulo"])
        st.write("**Descripción:**", noticia["descripcion"])
        st.write("**Contenido completo:**", noticia["contenido"] or "—")
        st.write("**Categoría:**", noticia["categoria"])
        st.write("**Fecha publicación:**", noticia["fecha_publicacion"])
        st.write("**Fuente:**", noticia["fuente_nombre"])
        if noticia["url_imagen"]:
            st.image(noticia["url_imagen"])
        st.markdown(f"[🔗 Enlace original]({noticia['url']})")
        st.form_submit_button("Aceptar")