from dataclasses import dataclass
import json
import os
from typing import List, Union
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


@dataclass
class EmbeddingsIdx:
    embeddings: List[torch.Tensor]
    ids: List[int]


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


def load_embeddings_from_db(db) -> EmbeddingsIdx:
    with db.conn:
        rephrased = db.query("select id, embedding from rephrased_questions")
        rephrased = list(rephrased)
        idx = EmbeddingsIdx(
            [torch.tensor(decode(r["embedding"])) for r in rephrased],
            [r["id"] for r in rephrased],
        )
        return idx


def load_embeddings_from_json(index_file: str) -> EmbeddingsIdx:
    with open(os.path.join(dirname, index_file)) as f:
        rephrased = json.loads(f.read())
        idx = EmbeddingsIdx(
            [torch.tensor(r["embeddings"]) for r in rephrased],
            [r["id"] for r in rephrased],
        )
    return idx


def find_most_similar_questions(idx: EmbeddingsIdx, question: str, top_k=5):
    closest_n = util.semantic_search(
        get_embeddings(question), idx.embeddings, top_k=top_k
    )[0]
    if closest_n:
        ids = [{"id": idx.ids[r["corpus_id"]], "score": r["score"]} for r in closest_n]
        return ids
    return []


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
