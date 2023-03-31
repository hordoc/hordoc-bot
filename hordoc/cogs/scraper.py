from collections import Counter
from dataclasses import asdict
from pprint import pprint as pp
from typing import List, Optional

import discord
from discord.ext import commands
from discord.ext.commands import Context

import sqlite_utils
from sqlite_utils.db import Table

from hordoc.data import (
    GuildItem,
    ForumChannelItem,
    ThreadItem,
    AuthorItem,
    MessageItem,
)


class Scraper(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        db: sqlite_utils.Database,
        guild_ids: List[int],
        forum_ids: List[int],
    ):
        self.bot = bot
        self.db = db
        self.guild_ids = guild_ids
        self.forum_ids = forum_ids
        self.stats: Counter = Counter()
        self.seen_authors: set[int] = set()

    async def scrape_thread(
        self, thread: discord.Thread, after_msg_id: Optional[int] = None
    ) -> Optional[int]:
        max_msg_id = after_msg_id
        t = ThreadItem.from_discord(thread)
        pp(t)
        Table(self.db, "threads").insert(asdict(t), pk="id", replace=True)
        if after_msg_id:
            # start from beginning, do incremental based on last known.
            after = discord.Object(after_msg_id)
        else:
            after = None
        async for message in thread.history(after=after, limit=None):
            if message.author.id not in self.seen_authors:
                print(f"Got a new author: {message.author}")
                self.seen_authors.add(message.author.id)
                a = AuthorItem.from_discord(message.author)
                pp(a)
                Table(self.db, "authors").insert(asdict(a), pk="id", replace=True)
                self.stats["authors"] += 1

            m = MessageItem.from_discord(message)
            pp(m)
            Table(self.db, "messages").insert(asdict(m), pk="id", replace=True)
            self.stats["messages"] += 1
            if max_msg_id is None or m.id > max_msg_id:
                max_msg_id = m.id
        return max_msg_id

    async def scrape_forum(self, forum: discord.ForumChannel) -> None:
        f = ForumChannelItem.from_discord(forum)
        pp(f)
        Table(self.db, "channels").insert(asdict(f), pk="id", replace=True)
        self.stats["forums"] += 1

        known_threads = {}
        for row in self.db.query(
            """
        select t.id as thread_id, max(m.id) as max_msg_id
        from threads t join messages m on t.id = m.channel_id
        where parent_id = :parent_id group by t.id
            """,
            {"parent_id": f.id},
        ):
            known_threads[row["thread_id"]] = row["max_msg_id"]

        async def potential_scrape_thread(
            thread: discord.Thread, stats_type: str
        ) -> None:
            if thread.id not in known_threads:
                print(f"Scraping new {stats_type} {thread.id}")
                max_msg_id = await self.scrape_thread(thread)
                self.stats["new_" + stats_type] += 1
                known_threads[thread.id] = max_msg_id
            elif thread.last_message_id > known_threads[thread.id]:
                print(
                    f"Scraping known {stats_type} {thread.id} with new messages {thread.last_message_id}"
                )
                max_msg_id = await self.scrape_thread(thread, known_threads[thread.id])
                self.stats["updated_" + stats_type] += 1
                known_threads[thread.id] = max_msg_id
            else:
                print(f"Skipping known {stats_type} {thread.id}")
                self.stats["skipped_" + stats_type] += 1

        for thread in forum.threads:
            await potential_scrape_thread(thread, "threads")
        async for thread in forum.archived_threads(limit=None):
            await potential_scrape_thread(thread, "archived_threads")

    async def scrape_guilds(self) -> Counter:
        self.stats.clear()

        guilds = [guild for guild in self.bot.guilds if guild.id in self.guild_ids]
        for guild in guilds:
            g = GuildItem.from_discord(guild)
            pp(g)
            Table(self.db, "guilds").insert(asdict(g), pk="id", replace=True)
            self.stats["guilds"] += 1

            for forum in guild.forums:
                if forum.id in self.forum_ids:
                    await self.scrape_forum(forum)
        return self.stats

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def scrape(
        self,
        ctx: Context,
    ) -> None:
        await ctx.send("Starting with scraping")
        stats = await self.scrape_guilds()
        await ctx.send(f"We are done with scraping!\n Statistics: {stats}")
