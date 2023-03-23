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
    pass
    """
    #parses the data and saves it to a json file
    d = []
    with open('rephrased.json') as f :
        rephrases = json.loads(f.read())
        for row in rephrases :
            parsed = {'id': row['id'], 'rephrased' : row['rephrased'], 'embeddings' : get_embeddings(row['rephrased']).tolist()}
            d.append(parsed)
        with (open('rephrased.json', 'w+')) as f :
            json.dump(d, f)
    """
    """
    processes a question from the json file

    """
