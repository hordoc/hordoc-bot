from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import discord
import sqlite_utils
from sqlite_utils.db import Table


def dt_to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


@dataclass
class GuildItem:
    """
    Dataclass for a Discord Guild (Server).
    Reference: https://discordpy.readthedocs.io/en/latest/api.html?highlight=message#discord.Guild
    """

    id: int
    name: str

    @staticmethod
    def from_discord(g: discord.Guild) -> "GuildItem":
        """
        Create a GuildItem from a `discord.Guild`.
        """
        return GuildItem(
            id=g.id,
            name=g.name,
        )


@dataclass
class ForumChannelItem:
    """
    Dataclass for a Discord ForumChannel.
    Reference: https://discordpy.readthedocs.io/en/latest/api.html?highlight=message#discord.ForumChannel
    """

    id: int
    guild_id: int
    name: str
    type: str

    @staticmethod
    def from_discord(f: discord.ForumChannel) -> "ForumChannelItem":
        """
        Create a ForumChannelItem from a `discord.ForumChannel`.
        """
        return ForumChannelItem(id=f.id, guild_id=f.guild.id, name=f.name, type="forum")


@dataclass
class ThreadItem:
    """
    Dataclass for a Discord Thread.
    Reference: https://discordpy.readthedocs.io/en/latest/api.html?highlight=message#discord.Thread
    """

    id: int
    parent_id: int
    owner_id: int
    name: str

    @staticmethod
    def from_discord(t: discord.Thread) -> "ThreadItem":
        """
        Create a ThreadItem from a `discord.Thread`.
        """
        return ThreadItem(
            id=t.id,
            parent_id=t.parent_id,
            owner_id=t.owner_id,
            name=t.name,
        )


@dataclass
class AuthorItem:
    """
    Dataclass for a Discord Author (Member).
    Reference: https://discordpy.readthedocs.io/en/latest/api.html?highlight=message#discord.Member

    TODO
    - nick
    - display_name
    - joined_at
    - avatar
    - roles
    """

    id: int
    name: str
    discriminator: str

    @staticmethod
    def from_discord(a: Union[discord.User, discord.Member]) -> "AuthorItem":
        """
        Create a MemberItem from a `discord.Member`.
        """
        return AuthorItem(
            id=a.id,
            name=a.name,
            discriminator=a.discriminator,
        )


@dataclass
class MessageItem:
    """
    Dataclass for a Discord Message.
    Reference: https://discordpy.readthedocs.io/en/latest/api.html?highlight=message#discord.Message

    TODO
    - reactions
    - reply_to
    """

    id: int
    channel_id: int  # this can be the channel or thread!
    created_at: int
    author_id: int
    content: str

    @staticmethod
    def from_discord(m: discord.Message) -> "MessageItem":
        """
        Create a MessageItem from a `discord.Message`.
        """
        return MessageItem(
            id=m.id,
            channel_id=m.channel.id,
            created_at=dt_to_ms(m.created_at),
            author_id=m.author.id,
            content=m.content,
        )


def find_answer_by_id(db: sqlite_utils.Database, id: int) -> Optional[str]:
    rows = db.query("select answer from answers where id = :id", {"id": id})
    return next(rows, {"answer": None})["answer"]


def find_rephrased_questions_by_ids(
    db: sqlite_utils.Database, ids: List[int]
) -> Dict[int, str]:
    rows = db.query(
        "select id, rephrased from rephrased_questions where id in (%s)"
        % (",".join("?" * len(ids))),
        ids,
    )
    return {r["id"]: r["rephrased"] for r in rows}


def log_questions(
    db: sqlite_utils.Database,
    id: int,
    user_id: str,
    question: str,
    answer: Optional[str],
    score: Optional[float],
    timestamp: Optional[int] = None,
) -> None:
    if timestamp is None:
        timestamp = dt_to_ms(datetime.utcnow())
    Table(db, "log_questions").insert(
        {
            "id": id,
            "timestamp": timestamp,
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "score": score,
        }
    )


def log_questions_feedback(
    db: sqlite_utils.Database,
    id: int,
    question_id: int,
    user_id: str,
    feedback: str,
    timestamp: Optional[int] = None,
) -> None:
    if timestamp is None:
        timestamp = dt_to_ms(datetime.utcnow())
    Table(db, "log_questions_feedback").insert(
        {
            "id": id,
            "question_id": question_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "feedback": feedback,
        }
    )


def _ensure_table(
    db: sqlite_utils.Database, table_name: str, *args: Any, **kwargs: Any
) -> None:
    if table_name not in db.table_names():
        Table(db, table_name).create(*args, **kwargs)


def ensure_tables(db: sqlite_utils.Database) -> None:
    # Create tables manually, because if we create them automatically
    # we may create items without 'title' first, which breaks
    # when we later call ensure_fts()
    _ensure_table(
        db,
        "guilds",
        {
            "id": int,
            "name": str,
        },
        pk="id",
        column_order=["id", "name"],
    )
    _ensure_table(
        db,
        "channels",
        {
            "id": int,
            "guild_id": int,
            "name": str,
            "type": str,
        },
        pk="id",
        column_order=["id", "guild_id", "name", "type"],
        foreign_keys=[("guild_id", "guilds", "id")],
    )
    _ensure_table(
        db,
        "authors",
        {
            "id": int,
            "name": str,
            "discriminator": str,
        },
        pk="id",
        column_order=["id", "name", "discriminator"],
    )
    _ensure_table(
        db,
        "threads",
        {
            "id": int,
            "parent_id": int,
            "owner_id": int,
            "name": str,
        },
        pk="id",
        column_order=["id", "parent_id", "owner_id", "name"],
        foreign_keys=[
            ("parent_id", "channels", "id"),
            ("owner_id", "authors", "id"),
        ],
    )
    _ensure_table(
        db,
        "messages",
        {
            "id": int,
            "channel_id": int,
            "created_at": int,
            "author_id": int,
            "content": str,
        },
        pk="id",
        column_order=["id", "channel_id", "name"],
        foreign_keys=[
            ("author_id", "authors", "id"),
        ],
    )
    _ensure_table(
        db,
        "rephrased_questions",
        {
            "id": int,
            "rephrased": str,
            "embedding": "blob",
        },
        pk="id",
        column_order=["id", "rephrased", "embedding"],
        foreign_keys=[
            ("id", "threads", "id"),
        ],
    )
    _ensure_table(
        db,
        "answers",
        {
            "id": int,
            "question": str,
            "answer": str,
            "messages": str,
        },
        pk="id",
        column_order=["id", "question", "answer", "messages"],
        foreign_keys=[
            ("id", "threads", "id"),
        ],
    )
    _ensure_table(
        db,
        "log_questions",
        {
            "id": int,
            "timestamp": int,
            "user_id": str,
            "question": str,
            "answer": str,
            "score": float,
        },
        pk="id",
    )
    _ensure_table(
        db,
        "log_questions_feedback",
        {
            "id": int,
            "question_id": int,
            "timestamp": int,
            "user_id": str,
            "feedback": str,
        },
        pk="id",
        foreign_keys=[
            ("question_id", "log_questions", "id"),
        ],
    )
