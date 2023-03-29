#!/usr/bin/env python3
import os
from typing import List, Optional

import discord
from discord.ext import commands
import sqlite_utils

from hordoc.cogs import questions, scraper


class HorDocBot(commands.Bot):
    # Sample from https://github.com/Rapptz/discord.py/blob/master/examples/advanced_startup.py

    def __init__(
        self,
        *args,
        # initial_extensions: List[str],
        db: sqlite_utils.Database,
        guilds_ids: List[int],
        forums_ids: List[int],
        status_channel_id: List[int],
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.db = db
        self.guilds_ids = guilds_ids
        self.forums_ids = forums_ids
        self.status_channel_id = status_channel_id
        self.testing_guild_id = testing_guild_id
        # self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:
        # here, we are loading extensions prior to sync to ensure we are syncing interactions defined in
        # those extensions.
        # for extension in self.initial_extensions:
        #     await self.load_extension(extension)

        # XXX We don't need Sync for now as we will self-register in the testing guild
        # await self.add_cog(sync.Sync(self))

        await self.add_cog(questions.Questions(self))
        await self.add_cog(scraper.Scraper(self))

        # In overriding setup hook,
        # we can do things that require a bot prior to starting to process events from the websocket.
        # In this case, we are using this to ensure that once connected, we sync for the testing guild.
        # You should not do this for every guild or for global sync, those should only be synced when
        # changes happen.
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)

            # Clear the command tree
            # self.tree.clear_commands(guild=None)
            # await self.tree.sync(guild=None)
            # self.tree.clear_commands(guild=guild)
            # await self.tree.sync(guild=guild)
            # print("Cleared command tree")

            # # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # # followed by syncing to the testing guild.
            print("Syncing command tree to test guild")
            await self.tree.sync(guild=guild)

        # This would also be a good place to connect to our database and
        # load anything that should be in memory prior to handling events.


def run_bot(db):
    guilds_ids = [
        int(guild_id) for guild_id in os.environ["DISCORD_GUILD_IDS"].split(",")
    ]
    forums_ids = [
        int(forum_id) for forum_id in os.environ["DISCORD_FORUM_IDS"].split(",")
    ]
    status_channel_id = int(os.environ["DISCORD_STATUS_CHANNEL_ID"])
    testing_guild_id = int(os.environ["DISCORD_TESTING_GUILD_ID"])

    assert len(guilds_ids), "Missing DISCORD_GUILD_IDS"
    assert len(forums_ids), "Missing DISCORD_FORUM_IDS"

    print(f"Guilds: {guilds_ids}")
    print(f"Forums: {forums_ids}")
    print(f"Status Channel: {status_channel_id}")

    intents = discord.Intents.default()
    intents.message_content = True
    client = HorDocBot(
        # initial_extensions=[],
        db=db,
        guilds_ids=guilds_ids,
        forums_ids=forums_ids,
        status_channel_id=status_channel_id,
        testing_guild_id=testing_guild_id,
        command_prefix="!",
        intents=intents,
    )
    client.run(os.environ["DISCORD_SECRET"])
