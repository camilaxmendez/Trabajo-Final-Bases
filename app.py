import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Credenciales de Supabase
url = "https://rhwfspmgxlvjvpwgrqdo.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJod2ZzcG1neGx2anZwd2dycWRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjQwODQsImV4cCI6MjA2NzQwMDA4NH0.cefHhgH8bwePEVXohFiykb46Zt849RoJshSiqzbYkbY"

supabase: Client = create_client(url, key)

st.title("Noticias desde Supabase")

# Leer datos de la tabla
response = supabase.table("noticias").select("*").execute()
data = response.data

df = pd.DataFrame(data)
st.dataframe(df)
