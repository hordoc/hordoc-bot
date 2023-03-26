import discord


class WasAnswerUsefulView(discord.ui.View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.answer = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.answer = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.answer = False
        self.stop()


opts = ["0", "1", "2", "3", "4", "None of the above"]
select_options = [discord.SelectOption(label=opt, value=opt) for opt in opts]


class SelectQuestionView(discord.ui.View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @discord.ui.select(options=select_options)
    async def select_question(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        self.stop()
