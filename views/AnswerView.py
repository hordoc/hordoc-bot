import discord


class WasAnswerUsefulView(discord.ui.View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.answer = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.answer = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.answer = False
        self.stop()


opts = ["0", "1", "2", "3", "4", "None of the above"]
select_options = [discord.SelectOption(label=opt, value=opt) for opt in opts]


class SelectQuestionView(discord.ui.View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @discord.ui.select(options=select_options)
    async def select_question(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        self.stop()
