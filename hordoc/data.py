from dataclasses import dataclass
from datetime import datetime

import discord


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
    def from_discord(a: discord.Member) -> "AuthorItem":
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


def ensure_tables(db):
    # Create tables manually, because if we create them automatically
    # we may create items without 'title' first, which breaks
    # when we later call ensure_fts()
    if "guilds" not in db.table_names():
        db["guilds"].create(
            {
                "id": int,
                "name": str,
            },
            pk="id",
            column_order=("id", "name"),
        )
    if "channels" not in db.table_names():
        # Can be forum channel or text channel
        db["channels"].create(
            {
                "id": int,
                "guild_id": int,
                "name": str,
                "type": str,
            },
            pk="id",
            column_order=("id", "guild_id", "name", "type"),
            foreign_keys=[("guild_id", "guilds", "id")],
        )
    if "authors" not in db.table_names():
        db["authors"].create(
            {
                "id": int,
                "name": str,
                "discriminator": str,
            },
            pk="id",
            column_order=("id", "name", "discriminator"),
        )
    if "threads" not in db.table_names():
        db["threads"].create(
            {
                "id": int,
                "parent_id": int,
                "owner_id": int,
                "name": str,
            },
            pk="id",
            column_order=("id", "parent_id", "owner_id", "name"),
            foreign_keys=[
                ("parent_id", "channels", "id"),
                ("owner_id", "authors", "id"),
            ],
        )
    if "messages" not in db.table_names():
        db["messages"].create(
            {
                "id": int,
                "channel_id": int,
                "created_at": int,
                "author_id": int,
                "content": str,
            },
            pk="id",
            column_order=("id", "channel_id", "name"),
            foreign_keys=[
                ("author_id", "authors", "id"),
            ],
        )
    if "rephrased_questions" not in db.table_names():
        db["rephrased_questions"].create(
            {
                "id": int,
                "rephrased": str,
                "embedding": "blob",
            },
            pk="id",
            column_order=("id", "rephrased", "embedding"),
            foreign_keys=[
                ("id", "threads", "id"),
            ],
        )
    if "answers" not in db.table_names():
        db["answers"].create(
            {
                "id": int,
                "question": str,
                "answer": str,
                "messages": str,
            },
            pk="id",
            column_order=("id", "question", "answer", "messages"),
            foreign_keys=[
                ("id", "threads", "id"),
            ],
        )
