import re

import streamlit as st
import requests  # pip install requests

def info_fuentes_form(fuente):
    with st.form("noticias_info"):
        st.write("**ID:**", fuente["id"])
        st.write("**ID API:**", fuente["id_api"])
        st.write("**Nombre:**", fuente["nombre"] or "—")
        st.write("**Descripción:**", fuente["descripcion"])
        st.markdown(f"[🔗 Enlace]({fuente['url']})")
        st.write("**Categoría:**", fuente["categoria"])
        st.write("**Lenguaje:**", fuente["lenguaje"])
        st.write("**País:**", fuente["pais"])

       
        st.form_submit_button("Aceptar")