import os
from typing import Any, List, Optional

import discord
from discord.ext import commands
import sqlite_utils

from hordoc.cogs import questions, scraper


class HorDocBot(commands.Bot):
    # Sample from https://github.com/Rapptz/discord.py/blob/master/examples/advanced_startup.py

    def __init__(
        self,
        *args: Any,
        # initial_extensions: List[str],
        db: sqlite_utils.Database,
        guild_ids: List[int],
        forum_ids: List[int],
        testing_guild_id: Optional[int] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.db = db
        self.guild_ids = guild_ids
        self.forum_ids = forum_ids
        self.testing_guild_id = testing_guild_id
        # self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:
        # here, we are loading extensions prior to sync to ensure we are syncing interactions defined in
        # those extensions.
        # for extension in self.initial_extensions:
        #     await self.load_extension(extension)

        # XXX We don't need Sync for now as we will self-register in the testing guild
        # await self.add_cog(sync.Sync(self))

        await self.add_cog(questions.Questions(self, self.db))
        await self.add_cog(
            scraper.Scraper(self, self.db, self.guild_ids, self.forum_ids)
        )

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


def run_bot(db: sqlite_utils.Database) -> None:
    guild_ids = [
        int(guild_id) for guild_id in os.environ["DISCORD_GUILD_IDS"].split(",")
    ]
    forum_ids = [
        int(forum_id) for forum_id in os.environ["DISCORD_FORUM_IDS"].split(",")
    ]
    testing_guild_id = int(os.environ["DISCORD_TESTING_GUILD_ID"])

    assert len(guild_ids), "Missing DISCORD_GUILD_IDS"
    assert len(forum_ids), "Missing DISCORD_FORUM_IDS"

    print(f"Guilds: {guild_ids}")
    print(f"Forums: {forum_ids}")

    intents = discord.Intents.default()
    intents.message_content = True
    client = HorDocBot(
        # initial_extensions=[],
        db=db,
        guild_ids=guild_ids,
        forum_ids=forum_ids,
        testing_guild_id=testing_guild_id,
        command_prefix="!",
        intents=intents,
    )
    client.run(os.environ["DISCORD_SECRET"])
