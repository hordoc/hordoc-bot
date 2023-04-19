from collections import Counter
from math import floor
from pprint import pprint as pp
import time
from torch import Tensor
from typing import Dict, List, Optional, Tuple, Union

import sqlite_utils
from sqlite_utils import Database
from sentence_transformers import SentenceTransformer, util

# from hordoc.embeddings.embeddings_search import find_most_similar, get_embeddings, EMBEDDINGS_MODEL
# Connect to the database file
db: Database = sqlite_utils.Database("../../data/horde_help.db")

# EMBEDDINGS_MODEL = "sentence-transformers/gtr-t5-large"
# EMBEDDINGS_MODEL = "intfloat/e5-large"
EMBEDDINGS_MODEL = "intfloat/e5-small"

model = SentenceTransformer(EMBEDDINGS_MODEL)


def get_embeddings(text: Union[list, str]) -> Tensor:
    return model.encode(text)


def score_bucket(x: float, base: int = 5) -> int:
    return base * floor(x / base)


guild_id = 781145214752129095
hours_backlog = 6
score_threshold = 0.5
time_delta_milliseconds = 1000 * 60 * 60 * hours_backlog


def get_messages_with_thanks_and_reply(db: Database) -> List[Dict]:
    excluded_users = ("db0", "Airic")
    query = f"""
    select chan_id, msg_id, uid, t, user, msg, r
    from horde_help
    where "msg" like "%thank%"
    and ("r" is not null and "r" != "")
    and "user" not in  {str(excluded_users)}
    order by msg_id"""
    return db.execute_returning_dicts(query)


def get_message_by_id(db: Database, msg_id: int) -> Optional[Dict]:
    query = f"""
    select chan_id, msg_id, uid, t, user, msg, r, te, re
    from horde_help
    where msg_id = {msg_id}
    order by msg_id"""
    result = db.execute_returning_dicts(query)
    if len(result) == 0:
        return None
    return result[0]


def get_messages_by_time_delta_and_uid(
    db: Database, start_time: int, delta: int, uid: int, channel_id: int
) -> List[Dict]:
    query = f"""
    select chan_id, msg_id, uid, t, user, msg
    from horde_help
    where t < {start_time}
    and t >= {start_time - delta}
    and uid = {uid}
    and chan_id = {channel_id}
    and msg like '%?%'
    order by msg_id"""
    return db.execute_returning_dicts(query)


def load_annotations(db: Database) -> Tuple[Dict, Counter]:
    annotations = {}
    counters: Counter[str] = Counter()

    for row in db.query(
        """
        select thx_msg_id, reply_msg_id, question_msg_id, label
        from horde_help_thx_annotations where label != ''
        """
    ):
        counters["total"] += 1
        if row["label"] == "OK":
            counters["ok"] += 1
        elif row["label"].startswith("SKIP"):
            counters["skip"] += 1
        # pp(row)
        annotations[row["thx_msg_id"]] = row
    return annotations, counters


def main() -> None:  # noqa: C901
    annotations, annotation_counters = load_annotations(db)
    counters: Counter[str] = Counter()

    def process_message(message: Dict) -> Optional[str]:
        if message["msg_id"] not in annotations:
            counters["ignore_no_annotation"] += 1
            return None
        annotation = annotations[message["msg_id"]]
        counters["messages_in"] += 1
        reply = get_message_by_id(db, message["r"])
        if reply is None:
            counters["skip_reply_not_found"] += 1
            counters["messages_skipped"] += 1
            return None
        if reply["uid"] == message["uid"]:
            counters["skip_reply_to_self"] += 1
            counters["messages_skipped"] += 1
            return None
        if reply["msg_id"] != annotation["reply_msg_id"]:
            counters["bad_reply_id"] += 1
            counters["messages_skipped"] += 1
            return None
        asker_messages = get_messages_by_time_delta_and_uid(
            db,
            int(message["t"]),
            time_delta_milliseconds,
            message["uid"],
            message["chan_id"],
        )
        if len(asker_messages) == 0:
            counters["skip_no_asker_messages"] += 1
            counters["messages_skipped"] += 1
            return None
        reply_embeddings = get_embeddings([reply["msg"]])[0]
        askers_messages_text = [m["msg"] for m in asker_messages]
        askers_messages_embeddings = get_embeddings(askers_messages_text)
        most_similars = util.semantic_search(
            reply_embeddings, askers_messages_embeddings, 5
        )[0]
        most_similars = list(
            filter(lambda m: m["score"] >= score_threshold, most_similars)
        )
        if len(most_similars) == 0:
            counters["skip_no_most_similars"] += 1
            counters["messages_skipped"] += 1
            return None
        most_similar_messages = [
            {"msg": asker_messages[m["corpus_id"]], "score": floor(m["score"] * 100)}
            for m in most_similars
        ]

        if annotation["label"] == "OK":
            counters["accurate_out"] += 1
            if (
                most_similar_messages[0]["msg"]["msg_id"]
                == annotation["question_msg_id"]
            ):
                counters["accurate_question"] += 1

        txt = (
            "LINK  : "
            f"https://discord.com/channels/{guild_id}/{message['chan_id']}/{message['msg_id']}\n"
        )
        q_bucket = score_bucket(most_similar_messages[0]["score"])
        counters[f"score_q{q_bucket}+"] += 1
        for m in most_similar_messages:
            txt += f"Q?{m['score']:3d}%  {m['msg']['msg']}\n"
        txt += f"REPLY : {reply['msg']}\n"
        txt += f"THANKS: {message['msg']}\n"
        txt += "-----------------\n"
        # print(asker_messages)
        counters["messages_out"] += 1
        return txt

    start = time.time()
    messages = get_messages_with_thanks_and_reply(db)
    with open("output.txt", "w", encoding="utf-8") as f:
        for message in messages:
            txt = process_message(message)
            if txt:
                print(txt)
                f.write(txt)

    end = time.time()

    stats = dict(
        parameters=dict(
            embeddings_model=EMBEDDINGS_MODEL,
            hours_backlog=hours_backlog,
            score_threshold=score_threshold,
        ),
        annotation_counters=dict(annotation_counters),
        counters=dict(counters),
        duration=end - start,
        accuracy_q=counters["accurate_question"] / annotation_counters["ok"],
        accuracy_out=counters["accurate_out"] / counters["messages_out"],
    )  # TODO fix based on real output or skip
    pp(stats)


if __name__ == "__main__":
    main()
