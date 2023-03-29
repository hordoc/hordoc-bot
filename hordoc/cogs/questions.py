import discord
from discord.ext import commands

from hordoc.embeddings.embeddings_search import (
    load_embeddings_from_db,
    find_most_similar_questions,
)
from hordoc.views import AnswerView


class Questions(commands.Cog):
    """
    Answers support questions.
    """

    def __init__(self, bot):
        self.bot = bot
        self.idx = load_embeddings_from_db(bot.db)

    @discord.app_commands.command(name="question", description="Ask something !")  # type: ignore
    @discord.app_commands.describe(question="Your question")
    async def question(self, interaction: discord.Interaction, question: str):
        print(f"Got a question: {question}")
        answer_certainty = 0.8
        await interaction.response.defer()
        try:
            qs = find_most_similar_questions(self.idx, question)

            if qs[0]["score"] > answer_certainty:
                # TODO move to data module
                rows = self.bot.db.query(
                    "select answer from answers where id = :id", qs[0]["id"]
                )
                a = next(rows)["answer"]
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

                # TODO move to data module
                ids = [q["id"] for q in qs]
                rows = self.bot.db.query(
                    "select id, rephrased from rephrased_questions where id in (%s)"
                    % (",".join("?" * len(ids))),
                    ids,
                )
                rephrased = {r["id"]: r["rephrased"] for r in rows}

                for i, q in enumerate(qs):
                    score_pct = round(q["score"] * 100)
                    str_to_send += (
                        f"#{i} - {q['id']} - {rephrased[q['id']]} ({score_pct} %)\n\n"
                    )
                str_to_send += "Is any of these questions what you were looking for ?"
                await interaction.followup.send(
                    str_to_send, view=AnswerView.SelectQuestionView()
                )
        except Exception as e:
            await interaction.followup.send(f"An error has occurred : {e}")
