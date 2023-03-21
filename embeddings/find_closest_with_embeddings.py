import faiss
import json
import numpy as np

data = json.load(open("embeddings.json"))

ids = data["ids"]

index = faiss.IndexFlatL2(len(data["embeddings"][0]))
index.add(np.array(data["embeddings"]))

def find_similar_for_id(id, k=10):
    idx = ids.index(id)
    embedding = data["embeddings"][idx]
    _, I = index.search(np.array([embedding]), k)
    # Now find the content IDs for the results
    return [ids[ix] for ix in I[0]]

# Example using id=6832
print(find_similar_for_id(6832))