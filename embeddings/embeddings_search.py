from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/gtr-t5-large")

def get_embeddings(text) :
    return model.encode(text)



