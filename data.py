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
    name: str

    @staticmethod
    def from_discord(f: discord.ForumChannel) -> "ForumChannelItem":
        """
        Create a ForumChannelItem from a `discord.ForumChannel`.
        """
        return ForumChannelItem(
            id=f.id,
            name=f.name,
        )


@dataclass
class ThreadItem:
    """
    Dataclass for a Discord Thread.
    Reference: https://discordpy.readthedocs.io/en/latest/api.html?highlight=message#discord.Thread
    """

    id: int
    name: str

    @staticmethod
    def from_discord(t: discord.Thread) -> "ThreadItem":
        """
        Create a ThreadItem from a `discord.Thread`.
        """
        return ThreadItem(
            id=t.id,
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
