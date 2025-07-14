from rake_nltk import Rake
import nltk

# === Función para extraer etiquetas ===
def extraer_etiquetas(texto, max_keywords=5):
    r = Rake()
    r.extract_keywords_from_text(texto)
    return r.get_ranked_phrases()

# === Función para insertar etiquetas y vincular con noticia ===
def insertar_etiquetas_para_noticia(id_noticia, texto_noticia):
    etiquetas = extraer_etiquetas(texto_noticia)
    
    print(etiquetas)

# === EJEMPLO DE USO ===
# Supón que ya insertaste esta noticia con ID 123
titulo = "El avance de la inteligencia artificial médica"
contenido = "La inteligencia artificial mejora el diagnóstico en hospitales modernos."
texto_completo = f"{titulo}. {contenido}"
id_noticia = 123  # ID real de la noticia en tu base de datos

insertar_etiquetas_para_noticia(id_noticia, texto_completo)
