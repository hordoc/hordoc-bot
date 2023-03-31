from typing import Any, Callable

import discord


class WasAnswerUsefulView(discord.ui.View):
    def __init__(self, callback_fn: Callable, **kwargs: Any):
        super().__init__(**kwargs)
        self.callback_fn = callback_fn

    async def handle_answer(
        self, interaction: discord.Interaction, feedback: str
    ) -> None:
        await interaction.response.send_message(
            "Thanks for your feedback!", ephemeral=True
        )
        await self.callback_fn(interaction, feedback)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await self.handle_answer(interaction, "YES")

    @discord.ui.button(label="Meh", style=discord.ButtonStyle.secondary)
    async def meh(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await self.handle_answer(interaction, "MEH")

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await self.handle_answer(interaction, "NO")


opts = ["0", "1", "2", "3", "4", "None of the above"]
select_options = [discord.SelectOption(label=opt, value=opt) for opt in opts]


class SelectQuestionView(discord.ui.View):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @discord.ui.select(options=select_options)
    async def select_question(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ) -> None:
        self.stop()
