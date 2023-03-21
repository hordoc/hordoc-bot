#!/usr/bin/env python3

import os
from pprint import pprint as pp

import discord

from data import GuildItem, ForumChannelItem, ThreadItem, AuthorItem, MessageItem
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents(68608)

client = discord.Client(intents=intents)
guilds_ids = [int(guild_id) for guild_id in os.environ["DISCORD_GUILD_IDS"].split(",")]
forums_ids = [int(forum_id) for forum_id in os.environ["DISCORD_FORUM_IDS"].split(",")]
status_channel_id = int(os.environ["DISCORD_STATUS_CHANNEL_ID"])

assert len(guilds_ids), "Missing DISCORD_GUILD_IDS"
assert len(forums_ids), "Missing DISCORD_FORUM_IDS"

print(f"Guilds: {guilds_ids}")
print(f"Forums: {forums_ids}")
print(f"Status Channel: {status_channel_id}")

# TODO
# Create data classes for
# guild
# forum_thread


@client.event
async def on_ready():
	print(f"We have logged in as {client.user}")
	#channels = await client.fetch_channels(
	#channel = await client.fetch_channel(status_channel_id)
	#await channel.send(f"The Doctor is in tha House!")

	seen_authors = set()

	#guilds = [guild for guild in client.guilds if guild.id in guilds_ids]
	forums = [await client.fetch_channel(forum_id) for forum_id in forums_ids]
	for forum in forums:
		f = ForumChannelItem.from_discord(forum)
		for thread in forum.threads:
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
