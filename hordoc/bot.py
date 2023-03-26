#!/usr/bin/env python3

from collections import Counter
from dataclasses import asdict
import os
from pprint import pprint as pp
from typing import List, Literal, Optional, cast

import discord
from discord.ext.commands import Greedy, Context
from discord.ext import commands
from dotenv import load_dotenv
import sqlite_utils

from hordoc.embeddings.embeddings_search import (
    find_most_similar_question,
    get_answer_for_question,
)
from hordoc.data import (
    GuildItem,
    ForumChannelItem,
    ThreadItem,
    AuthorItem,
    MessageItem,
    ensure_tables,
)
from hordoc.views import AnswerView

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)
guilds_ids = [int(guild_id) for guild_id in os.environ["DISCORD_GUILD_IDS"].split(",")]
forums_ids = [int(forum_id) for forum_id in os.environ["DISCORD_FORUM_IDS"].split(",")]
status_channel_id = int(os.environ["DISCORD_STATUS_CHANNEL_ID"])

assert len(guilds_ids), "Missing DISCORD_GUILD_IDS"
assert len(forums_ids), "Missing DISCORD_FORUM_IDS"

print(f"Guilds: {guilds_ids}")
print(f"Forums: {forums_ids}")
print(f"Status Channel: {status_channel_id}")

db = sqlite_utils.Database(os.environ["DB_PATH"])


async def scrape_guilds() -> Counter:
    stats: Counter = Counter()
    seen_authors = set()

    async def scrape_thread(thread):
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
                stats["authors"] += 1

            m = MessageItem.from_discord(message)
            pp(m)
            db["messages"].insert(asdict(m), pk="id", replace=True)
            stats["messages"] += 1

    # Can this be done more efficiently without causing mypy to trip?
    guilds_table = cast(sqlite_utils.db.Table, db.table("guilds"))
    channels_table = cast(sqlite_utils.db.Table, db.table("channels"))

    guilds = [guild for guild in client.guilds if guild.id in guilds_ids]
    for guild in guilds:
        g = GuildItem.from_discord(guild)
        pp(g)
        guilds_table.insert(asdict(g), pk="id", replace=True)
        stats["guilds"] += 1

        forums = [channel for channel in guild.forums if channel.id in forums_ids]
        for forum in forums:
            f = ForumChannelItem.from_discord(forum)
            pp(f)
            channels_table.insert(asdict(f), pk="id", replace=True)
            stats["forums"] += 1
            for thread in forum.threads:
                await scrape_thread(thread)
                stats["threads"] += 1

            async for thread in forum.archived_threads(limit=None):
                await scrape_thread(thread)
                stats["archived_threads"] += 1
    return stats


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

    # stats = await scrape_guilds()

    # print("We are done with scraping!")
    # print("Statistics: ", stats)
    # await client.close()


@client.tree.command(name="question", description="Ask something !")
@discord.app_commands.describe(question="Your question")
async def question(interaction: discord.Interaction, question: str):
    answer_certainty = 0.8
    await interaction.response.defer()
    try:
        q = find_most_similar_question(question)
        if q[0]["score"] > answer_certainty:
            a = get_answer_for_question(q[0]["text"])
            await interaction.followup.send(
                "Your question was : "
                + question
                + "\n\nAnswer : "
                + a
                + "\n\nWas this answer useful ?",
                view=AnswerView.WasAnswerUsefulView(),
            )
            return
        else:
            str_to_send = (
                "Sorry, but i didn't find anything satisfying enough to answer you. \nYour question was : "
                + question
                + "\nThe most similar questions are :  \n\n"
            )
            for i, item in enumerate(q):
                str_to_send += f"{str(i)} - {str(item['text'])} ({str(round(item['score']* 100))} % ) \n\n"
            str_to_send += "Is any of these questions what you were looking for ?"
            await interaction.followup.send(
                str_to_send, view=AnswerView.SelectQuestionView()
            )
    except Exception as e:
        await interaction.followup.send(f"An error has occurred : {e}")


@client.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
    ctx: Context,
    guilds: Greedy[List[discord.Object]],
    spec: Optional[Literal["~", "*", "^"]] = None,
) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


if __name__ == "__main__":
    ensure_tables(db)
    client.run(os.environ["DISCORD_SECRET"])
