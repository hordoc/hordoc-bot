import discord
from discord.ext import commands

from hordoc.embeddings.embeddings_search import (
    find_most_similar_question,
    get_answer_for_question,
)
from hordoc.views import AnswerView


class Questions(commands.Cog):
    """
    Answers support questions.
    """

    def __init__(self, bot):
        self.bot = bot

    # @commands.command()  # type: ignore
    @discord.app_commands.command(name="question", description="Ask something !")  # type: ignore
    @discord.app_commands.describe(question="Your question")
    async def question(self, interaction: discord.Interaction, question: str):
        print(f"Got a question: {question}")
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
                    "Sorry, but i didn't find anything satisfying enough to answer you.\n"
                    "Your question was : "
                    + question
                    + "\nThe most similar questions are :  \n\n"
                )
                for i, item in enumerate(q):
                    str_to_send += f"{i} - {str(item['text'])} ({round(item['score']* 100)} % ) \n\n"
                str_to_send += "Is any of these questions what you were looking for ?"
                await interaction.followup.send(
                    str_to_send, view=AnswerView.SelectQuestionView()
                )
        except Exception as e:
            await interaction.followup.send(f"An error has occurred : {e}")
