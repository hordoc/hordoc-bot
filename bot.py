#!/usr/bin/env python3

from dataclasses import asdict
import os
from pprint import pprint as pp
from dotenv import load_dotenv
import discord
import sqlite_utils

from data import (
    GuildItem,
    ForumChannelItem,
    ThreadItem,
    AuthorItem,
    MessageItem,
    ensure_tables,
)


load_dotenv()
intents = discord.Intents.default()

client = discord.Client(intents=intents)
guilds_ids = [int(guild_id) for guild_id in os.environ["DISCORD_GUILD_IDS"].split(",")]
forums_ids = [int(forum_id) for forum_id in os.environ["DISCORD_FORUM_IDS"].split(",")]
status_channel_id = int(os.environ["DISCORD_STATUS_CHANNEL_ID"])

assert len(guilds_ids), "Missing DISCORD_GUILD_IDS"
assert len(forums_ids), "Missing DISCORD_FORUM_IDS"

print(f"Guilds: {guilds_ids}")
print(f"Forums: {forums_ids}")
print(f"Status Channel: {status_channel_id}")

# TODO make configurable, move db to context
DB_PATH = "data/mikex_workshop.db"
db = sqlite_utils.Database(DB_PATH)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    # channel = await client.fetch_channel(status_channel_id)
    # await channel.send(f"The Doctor is in tha House!")

    seen_authors = set()

    guilds = [guild for guild in client.guilds if guild.id in guilds_ids]
    for guild in guilds:
        g = GuildItem.from_discord(guild)
        pp(g)
        db["guilds"].insert(asdict(g), pk="id", replace=True)

        forums = [channel for channel in guild.forums if channel.id in forums_ids]
        for forum in forums:
            f = ForumChannelItem.from_discord(forum)
            pp(f)
            db["channels"].insert(asdict(f), pk="id", replace=True)
            threads = forum.threads
            for thread in threads:
                t = ThreadItem.from_discord(thread)
                pp(t)
                db["threads"].insert(asdict(t), pk="id", replace=True)
                # TODO start from beginning, do incremental based on last known.
                async for message in thread.history():
                    if message.author.id not in seen_authors:
                        print(f"Got a new author: {message.author}")
                        seen_authors.add(message.author.id)
                        a = AuthorItem.from_discord(message.author)
                        pp(a)
                        db["authors"].insert(asdict(a), pk="id", replace=True)

                    m = MessageItem.from_discord(message)
                    pp(m)
                    db["messages"].insert(asdict(m), pk="id", replace=True)

    print("We are done with scraping!")
    await client.close()


@client.event
async def on_message(message):
    pass


if __name__ == "__main__":
    ensure_tables(db)
    client.run(os.environ["DISCORD_SECRET"])
