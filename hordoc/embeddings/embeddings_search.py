import json
import os
from typing import Union
import struct

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
import torch
import openai

load_dotenv()

EMBEDDINGS_MODEL = "sentence-transformers/gtr-t5-large"
GPT_MODEL = "gpt-3.5-turbo"
SIMILARITY_THRESHOLD = 0.8

dirname = os.path.dirname(__file__)
model = SentenceTransformer(EMBEDDINGS_MODEL)


def decode(blob):
    """Decode blob into vector of floats."""
    return struct.unpack("f" * (len(blob) // 4), blob)


def encode(vector):
    """Encode vector of floats into blob."""
    return struct.pack("f" * len(vector), *vector)


def get_embeddings(text: Union[list, str]):
    return model.encode(text)


# unused
def find_most_similar(text, corpus, top_k=5):
    corpus_embeddings = get_embeddings(corpus)
    query_embedding = get_embeddings([text])
    closest_n = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)
    best_score = closest_n[0]["score"]
    if best_score < SIMILARITY_THRESHOLD:
        print("best_score", best_score)
        return []
    return closest_n


def find_most_similar_question(question):
    with open(os.path.join(dirname, "rephrased.json")) as f:
        rephrased = json.loads(f.read())
        embeddings = [torch.tensor(r["embeddings"]) for r in rephrased]
        closest_n = util.semantic_search(get_embeddings(question), embeddings, top_k=5)[
            0
        ]
        if closest_n:
            ids = [{"id": r["corpus_id"], "score": r["score"]} for r in closest_n]
            data = [
                {"text": rephrased[i["id"]]["rephrased"], "score": i["score"]}
                for i in ids
            ]
            print("data", data)
            return data
        return []


def get_answer_for_question(question):
    with open(os.path.join(dirname, "answers.json")) as f:
        d = json.loads(f.read())
        for row in d:
            print(row["question"], question)
            if row["question"] == question:
                return row["answer"]
        return (
            "Sorry, I don't know the answer to that question. Try asking in the forum."
        )


def rephrase_question(question, text):
    if openai.api_key is None:
        openai.api_key = os.environ["OPENAI_API_KEY"]

    prompt = f"""
    Title: {question}
    Content: {text}
    Given the above question and context, what is the best way to rephrase the question? Answer in one sentence.
    """  # noqa: E501
    data = [
        {"role": "system", "content": "Execute the following task :"},
        {"role": "user", "content": prompt},
    ]
    return (
        openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=data,
            temperature=0,
            max_tokens=500,
        )
        .choices[0]
        .message.content.strip()
    )


if __name__ == "__main__":
    # URL TO GET ALL POSTS
    pass
    """
    #parses the data and saves it to a json file
    d = []
    with open('rephrased.json') as f :
        rephrases = json.loads(f.read())
        for row in rephrases :
            parsed = {
                'id': row['id'], 'rephrased' : row['rephrased'],
                'embeddings' : get_embeddings(row['rephrased']).tolist()}
            d.append(parsed)
        with (open('rephrased.json', 'w+')) as f :
            json.dump(d, f)
    """
    """
    processes a question from the json file

    """
