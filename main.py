import streamlit as st

# --- PAGE SETUP ---
dashboard_page = st.Page(
    page = "pages/dashboard.py",
    title = "Dashboard",
    icon=":material/dashboard:",
    default=True
)

fuentes_page = st.Page(
    page = "pages/ver_fuentes.py",
    title = "Fuentes",
    icon=":material/article_person:"
)

noticias_page = st.Page(
    page = "pages/ver_noticias.py",
    title = "Noticias",
    icon=":material/newspaper:"
)

analisis_fuentes_page = st.Page(
    page = "pages/analisis_fuentes.py",
    title = "Análisis de fuentes",
    icon=":material/account_tree:"
)

sentimientos_page = st.Page(
    page = "pages/analisis_sentimientos.py",
    title = "Análisis de sentimientos",
    icon=":material/mood:"
)

etiquetas_page = st.Page(
    page = "pages/consulta_etiquetas.py",
    title = "Consulta de etiquetas",
    icon=":material/sell:"
)


# pg = st.navigation(pages=[fuentes_page, noticias_page])
# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Principal": [dashboard_page, noticias_page, fuentes_page],
        "Analisis": [analisis_fuentes_page, etiquetas_page, sentimientos_page]
    }
)

# --- SHARED ON ALL PAGES ---
#st.logo("assets/codingisfun_logo.png")
st.sidebar.text("Realizado por: Camila Méndez y Carlos Gómez")

pg.run()
