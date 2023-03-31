from collections import Counter
from dataclasses import asdict
from pprint import pprint as pp

import discord
from discord.ext import commands
from discord.ext.commands import Context

from sqlite_utils.db import Table

from hordoc.bot import HorDocBot
from hordoc.data import (
    GuildItem,
    ForumChannelItem,
    ThreadItem,
    AuthorItem,
    MessageItem,
)


class Scraper(commands.Cog):
    """
    Syncs the command tree.
    From https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f
    """

    def __init__(self, bot: HorDocBot):
        self.bot = bot

    async def scrape_guilds(self) -> Counter:
        stats: Counter = Counter()
        seen_authors = set()

        async def scrape_thread(thread: discord.Thread) -> None:
            t = ThreadItem.from_discord(thread)
            pp(t)
            Table(self.bot.db, "threads").insert(asdict(t), pk="id", replace=True)
            # TODO start from beginning, do incremental based on last known.
            async for message in thread.history():
                if message.author.id not in seen_authors:
                    print(f"Got a new author: {message.author}")
                    seen_authors.add(message.author.id)
                    a = AuthorItem.from_discord(message.author)
                    pp(a)
                    Table(self.bot.db, "authors").insert(
                        asdict(a), pk="id", replace=True
                    )
                    stats["authors"] += 1

                m = MessageItem.from_discord(message)
                pp(m)
                Table(self.bot.db, "messages").insert(asdict(m), pk="id", replace=True)
                stats["messages"] += 1

        guilds = [guild for guild in self.bot.guilds if guild.id in self.bot.guilds_ids]
        for guild in guilds:
            g = GuildItem.from_discord(guild)
            pp(g)
            Table(self.bot.db, "guilds").insert(asdict(g), pk="id", replace=True)
            stats["guilds"] += 1

            forums = [
                channel for channel in guild.forums if channel.id in self.bot.forums_ids
            ]
            for forum in forums:
                f = ForumChannelItem.from_discord(forum)
                pp(f)
                Table(self.bot.db, "channels").insert(asdict(f), pk="id", replace=True)
                stats["forums"] += 1
                for thread in forum.threads:
                    await scrape_thread(thread)
                    stats["threads"] += 1

                async for thread in forum.archived_threads(limit=None):
                    await scrape_thread(thread)
                    stats["archived_threads"] += 1
        return stats

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
