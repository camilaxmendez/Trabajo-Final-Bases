from keybert import KeyBERT

kw_model = KeyBERT()
keywords = kw_model.extract_keywords("The 55-inch Hisense U7 is a great 4K TV under $600 for Prime Day")
print(keywords)