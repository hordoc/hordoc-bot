import discord
from discord.ext import commands

from hordoc.bot import HorDocBot
from hordoc.data import (
    find_answer_by_id,
    # find_rephrased_questions_by_ids,
    log_questions,
    log_questions_feedback,
)
from hordoc.embeddings.embeddings_search import (
    load_embeddings_from_db,
    find_most_similar_questions,
)
from hordoc.views import AnswerView


class Questions(commands.Cog):
    """
    Answers support questions.
    """

    def __init__(self, bot: HorDocBot):
        self.bot = bot
        self.idx = load_embeddings_from_db(bot.db)

    @discord.app_commands.command(name="question", description="Ask something !")  # type: ignore
    @discord.app_commands.describe(question="Your question")
    async def question(self, interaction: discord.Interaction, question: str):
        print(f"Got a question: {question}")
        await interaction.response.defer()

        qs = find_most_similar_questions(self.idx, question)
        # TODO check that we got atleast 1 question
        score = qs[0]["score"]
        score_pct = round(score * 100)

        # answer_certainty = 0.8
        # if qs[0]["score"] > answer_certainty:
        answer = find_answer_by_id(self.bot.db, qs[0]["id"])
        log_questions(
            self.bot.db, interaction.id, str(interaction.user), question, answer, score
        )

        async def answer_view_callback(
            feedback_interaction: discord.Interaction, feedback: str
        ) -> None:
            print(f"The feedback by {feedback_interaction.user} was {feedback}")
            log_questions_feedback(
                self.bot.db,
                feedback_interaction.id,
                interaction.id,
                str(feedback_interaction.user),
                feedback,
            )

        view = AnswerView.WasAnswerUsefulView(answer_view_callback, timeout=3600.0)
        await interaction.followup.send(
            f"Question: {question}\n\nAnswer (score {score_pct}%): {answer}\n\nWas this answer useful?",
            suppress_embeds=True,
            view=view,
        )
        # else:
        #     str_to_send = (
        #         "Sorry, but i didn't find anything satisfying enough to answer you.\n"
        #         "Your question was : "
        #         + question
        #         + "\nThe most similar questions are :  \n\n"
        #     )

        #     ids = [q["id"] for q in qs]
        #     rephrased = find_rephrased_questions_by_ids(self.bot.db, ids)

        #     for i, q in enumerate(qs):
        #         score_pct = round(q["score"] * 100)
        #         str_to_send += (
        #             f"#{i} - {q['id']} - {rephrased[q['id']]} ({score_pct} %)\n\n"
        #         )
        #     str_to_send += "Is any of these questions what you were looking for ?"
        #     await interaction.followup.send(
        #         str_to_send, view=AnswerView.SelectQuestionView()
        #     )

    # except Exception as e:
    #     await interaction.followup.send(f"An error has occurred : {e}")
