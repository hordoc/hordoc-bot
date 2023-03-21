#!/usr/bin/env python3

import os
from pprint import pprint as pp

import discord

from data import GuildItem, ForumChannelItem, ThreadItem, AuthorItem, MessageItem


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
guilds_ids = [int(guild_id) for guild_id in os.environ["DISCORD_GUILD_IDS"].split(",")]
forums_ids = [int(forum_id) for forum_id in os.environ["DISCORD_FORUM_IDS"].split(",")]
status_channel_id = int(os.environ["DISCORD_STATUS_CHANNEL_ID"])

assert len(guilds_ids), "Missing DISCORD_GUILD_IDS"
assert len(forums_ids), "Missing DISCORD_FORUM_IDS"

# TODO
# Create data classes for
# guild
# forum_thread


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

    # channel = client.get_channel(status_channel_id)
    # await channel.send(f"The Doctor is in tha House!")

    seen_authors = set()

    guilds = [guild for guild in client.guilds if guild.id in guilds_ids]
    for guild in guilds:
        g = GuildItem.from_discord(guild)
        pp(g)
        forums = [channel for channel in guild.forums if channel.id in forums_ids]
        for forum in forums:
            f = ForumChannelItem.from_discord(forum)
            pp(f)
            threads = forum.threads
            for thread in threads:
                t = ThreadItem.from_discord(thread)
                pp(t)
                # TODO start from beginning, do incremental based on last known.
                async for message in thread.history():
                    if message.author.id not in seen_authors:
                        print(f"Got a new author: {message.author}")
                        seen_authors.add(message.author.id)
                        a = AuthorItem.from_discord(message.author)
                        pp(a)

                    m = MessageItem.from_discord(message)
                    pp(m)

    print("We are done with scraping!")
    await client.close()


@client.event
async def on_message(message):
    pass


if __name__ == "__main__":
    client.run(os.environ["DISCORD_SECRET"])
