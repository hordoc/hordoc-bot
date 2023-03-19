#!/usr/bin/env python3

import os

import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
guilds_ids = [int(guild_id) for guild_id in os.environ["DISCORD_GUILD_IDS"].split(",")]
forums_ids = [int(forum_id) for forum_id in os.environ["DISCORD_FORUM_IDS"].split(",")]
status_channel_id = int(os.environ["DISCORD_STATUS_CHANNEL_ID"])


assert len(guilds_ids), "Missing DISCORD_GUILD_IDS"
assert len(forums_ids), "Missing DISCORD_FORUM_IDS"


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

    # channel = client.get_channel(status_channel_id)
    # await channel.send(f"The Doctor is in tha House!")

    guilds = [guild for guild in client.guilds if guild.id in guilds_ids]
    for guild in guilds:
        forums = [channel for channel in guild.forums if channel.id in forums_ids]
        for forum in forums:
            threads = forum.threads
            for thread in threads:
                thread_name = thread.name
                print(f"Thread name: {thread_name}")

                async for message in thread.history():
                    print(f"Message: {message.content}")


@client.event
async def on_message(message):
    pass


client.run(os.environ["DISCORD_SECRET"])
