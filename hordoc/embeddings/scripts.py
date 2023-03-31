import json
import os
from typing import Any, Dict, List, Optional, Tuple
import urllib.parse

import openai
import requests
from sentence_transformers import util
import torch

from .embeddings_search import get_embeddings, rephrase_question


DB_URL = "https://horde-qna-db.spevktator.io"
GPT_MODEL = "gpt-3.5-turbo"

openai.api_key = os.environ["OPENAI_API_KEY"]


def find_closest_question(
    question: str, rows: List[List[int]], threshold: float = 0.8
) -> List[int]:
    with open("./embeddings.json") as f:
        question = "I have kudos but cant generate the image"
        question_embedding = get_embeddings(question)
        contents = json.loads(f.read())
        embeddings = [torch.tensor(c["embeddings"]) for c in contents]

        closest_n = util.semantic_search(question_embedding, embeddings, top_k=5)
        print(closest_n[0])

        best_score = closest_n[0][0]["score"]
        ids = [c["corpus_id"] for c in closest_n[0]]
        db_ids = [contents[i]["id"] for i in ids]
        questions = [row for row in rows if row[0] in db_ids]
        if best_score < threshold:
            print("threshold not met : ", best_score)
        return questions[0]


def rephrase_from_db(
    rows: List[Tuple[int, str, str, str]], save_to_file: bool = False
) -> List[Dict[str, Any]]:
    rephrased = [
        {"id": row[0], "rephrased": rephrase_question(row[2], row[3])} for row in rows
    ]
    if save_to_file:
        with open("rephrased.json", "w+") as f:
            json.dump(rephrased, f)
    return rephrased


def get_channel_ids() -> List[int]:
    with open("rephrased.json") as f:
        contents = json.loads(f.read())
        return [c["id"] for c in contents]


def get_channel_question_embeddings(channel_ids: List[int]) -> List[torch.Tensor]:
    with open("rephrased.json") as f:
        contents = json.loads(f.read())
        embeddings = [
            torch.tensor(c["embeddings"]) for c in contents if c["id"] in channel_ids
        ]
        return embeddings


def get_channel_messages(channel_id: int) -> List[str]:
    sql = "select id, content from messages where channel_id = :p0 order by id desc limit 101"
    params = urllib.parse.urlencode({"sql": sql, "channel_id": channel_id})
    url = f"{DB_URL}/horde_support.json?{params}"

    data = requests.get(url).json()
    messages = [d for d in data["rows"] if d[0] != channel_id]
    return messages


def build_channels_embeddings() -> None:
    channel_ids = get_channel_ids()
    embeddings_list = []
    with open("channel_embeddings.json", "r+") as f:
        for channel_id in channel_ids:
            messages = get_channel_messages(channel_id)
            messages_text = [m[1] for m in messages if m[0] != channel_id]
            embeddings = get_embeddings(messages_text)
            embedding = [
                {"message_id": messages[i][0], "embeddings": e.tolist()}
                for i, e in enumerate(embeddings)
            ]
            embeddings_list.append({"channel_id": channel_id, "embeddings": embedding})
    with open("channel_embeddings.json", "w+") as f:
        json.dump(embeddings_list, f)


def get_channel_answers_embeddings(channel_id: int) -> List[Dict[str, Any]]:
    with open("channel_embeddings.json") as f:
        contents = json.loads(f.read())
        channel = [c for c in contents if c["channel_id"] == channel_id][0]
        embeddings = [
            {"id": c["message_id"], "embeddings": torch.tensor(c["embeddings"])}
            for c in channel["embeddings"]
        ]
        return embeddings


def get_question_embeddings_for_channel(channel_id: int) -> List[torch.Tensor]:
    with open("rephrased.json") as f:
        contents = json.loads(f.read())
        embeddings = [
            torch.tensor(c["embeddings"]) for c in contents if c["id"] == channel_id
        ]
        return embeddings


def get_questions_for_channel(channel_id: int) -> List[str]:
    with open("rephrased.json") as f:
        contents = json.loads(f.read())
        questions = [c["rephrased"] for c in contents if c["id"] == channel_id]
        return questions


def build_answer(question: str, corpus: List[str]) -> str:
    prompt = f"""
Using this data :
{corpus}
Formulate an answer to this question :
{question}
Include relevant urls if they are known
"""
    print(prompt)
    data = [
        {"role": "system", "content": "Execute the following task :"},
        {"role": "user", "content": prompt},
    ]
    return str(
        openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=data,
            temperature=0,
            max_tokens=500,
        )
        .choices[0]
        .message.content.strip()
    )


def build_channel_response(channel_id: int) -> Optional[str]:
    print(channel_id)
    messages = get_channel_messages(channel_id)
    if len(messages) < 2:
        return None
    print(messages)
    embeddings = get_channel_answers_embeddings(channel_id)
    embeddings_only = [e["embeddings"] for e in embeddings]
    question_embeddings = get_question_embeddings_for_channel(channel_id)
    closest_n = util.semantic_search(question_embeddings, embeddings_only, top_k=5)
    closest_n_ids = [embeddings[c["corpus_id"]]["id"] for c in closest_n[0]]

    print(closest_n_ids)
    closest_n_messages = [
        message for message in messages if message[0] in closest_n_ids
    ]

    closest_n_messages_text = [m[1] for m in closest_n_messages]
    print(closest_n_messages_text)
    questions = get_questions_for_channel(channel_id)
    print()
    print(questions)
    answer = build_answer(questions[0], closest_n_messages_text)
    return answer


if __name__ == "__main__":
    pass

"""
channel_id = '1021208495414071307'
url = (
    'https://horde-qna-db.spevktator.io/horde_support.json?'
    '?sql=select+id%2C+content+from+messages+where+%22channel_id%22+%3D+%3Ap0+order+by+id+desc+limit+101'
    '&p0=1021208495414071307')
data = requests.get(url).json()
messages = [d[1] for d in data['rows']]
#print(messages[0])
question = (
    'What is the recommended method for joining the horde and contributing to the parallelization'
    ' of GPU processing for the benefit of others?')
question_embedding = get_embeddings(question)
embeddings = get_embeddings(messages)
closest_n = util.semantic_search(question_embedding, embeddings, top_k=10)
#print(closest_n)
ids = [c['corpus_id'] for c in closest_n[0]]
closest_n_text = [messages[i] for i in ids]
for i in closest_n_text :
    print(i)
    print('---------------------')
"""
