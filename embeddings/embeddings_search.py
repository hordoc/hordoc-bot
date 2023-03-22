from sentence_transformers import SentenceTransformer
from sentence_transformers import util
from dotenv import load_dotenv
load_dotenv('../.env')
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



def rephrase_question(question, text) :
    import openai
    import os
    openai.api_key = os.environ["OPENAI_API_KEY"]
    prompt = f"""
    Title: {question}
    Content: {text}
    Given the above question and context, what is the best way to rephrase the question? Answer in one sentence.
    """
    data = [
				{"role": "system", "content": 'Execute the following task :'},
				{"role": "user", "content": prompt}
		]
    return openai.ChatCompletion.create(
			model="gpt-3.5-turbo",
			messages=data,
			temperature=0,
			max_tokens=500,
		).choices[0].message.content.strip()

if __name__ == "__main__":
    # URL TO GET ALL POSTS
    url = 'https://horde-qna-db.spevktator.io/horde_support.json?sql=select+threads.id%2C+datetime%28round%28messages.created_at+%2F+1000%29%2C+%27unixepoch%27%29+as+timestamp%2C+threads.name%2C+content+from+threads+join+messages+on+threads.id+%3D+messages.id+order+by+timestamp+desc'

    import requests
    import json
    data = requests.get(url).json()
    rows = data['rows']
    print(rows[0])

    rephrased = [{'id' : row[0] ,'rephrased' : rephrase_question(row[2],row[3])} for row in rows]
    with open('rephrased.json', 'w+') as f :
        json.dump(rephrased, f)
    """
    parses the data and saves it to a json file
    d = []
    for row in rows :
        parsed = {'id': row[0], 'embeddings' : get_embeddings(row[2]).tolist()}
        d.append(parsed)
    with (open('embeddings.json', 'w+')) as f :
        json.dump(d, f)
    """
    """
    processes a question from the json file
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
    """
