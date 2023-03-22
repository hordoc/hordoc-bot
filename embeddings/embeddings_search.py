from sentence_transformers import SentenceTransformer
from sentence_transformers import util
import torch
model = SentenceTransformer("sentence-transformers/gtr-t5-large")
threshold = 0.8


def get_embeddings(text : list or str) :
    return model.encode(text)

def find_most_similar(text, corpus, top_k=5) :
    corpus_embeddings = get_embeddings(corpus)
    query_embedding = get_embeddings([text])
    closest_n = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)
    best_score = closest_n[0]['score']
    if best_score < threshold :
        print('best_score', best_score)
        return []
    return closest_n


if __name__ == "__main__":
    url = 'https://horde-qna-db.spevktator.io/horde_support.json?sql=select+threads.id%2C+datetime%28round%28messages.created_at+%2F+1000%29%2C+%27unixepoch%27%29+as+timestamp%2C+threads.name%2C+content+from+threads+join+messages+on+threads.id+%3D+messages.id+order+by+timestamp+desc'
    import requests
    import json
    data = requests.get(url).json()
    rows = data['rows']
    #d = []
    #for row in rows :
    #    parsed = {'id': row[0], 'embeddings' : get_embeddings(row[3]).tolist()}
    #    d.append(parsed)
    #with (open('embeddings.json', 'w+')) as f :
    #    json.dump(d, f)
    with open('./embeddings.json') as f :
        question = 'I have kudos but cant generate the image'
        question_embedding = get_embeddings(question)
        contents= json.loads(f.read())
        embeddings = [torch.tensor(c['embeddings']) for c in contents]

        closest_n = util.semantic_search(question_embedding, embeddings, top_k=5)
        print(closest_n[0])

        best_score = closest_n[0][0]['score']
        ids = [c['corpus_id'] for c in closest_n[0]]
        db_ids = [contents[i]['id'] for i in ids]
        questions = [row for row in rows if row[0] in db_ids]
        if best_score < threshold :
            print('threshold not met : ', best_score)
        print(questions)