#!/usr/bin/env python3

import json

from dotenv import load_dotenv
import click
import sqlite_utils
from tabulate import tabulate

from hordoc.bot import run_bot
from hordoc.data import (
    ensure_tables,
    find_answer_by_id,
    find_rephrased_questions_by_ids,
)
from hordoc.embeddings.embeddings_search import (
    encode,
    load_embeddings_from_db,
    find_most_similar_questions,
)


load_dotenv()


@click.group()
@click.version_option()
def cli():
    "HorDoc: AI-Powered Discord Community Support"


# TODO make db_path a common argument


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
def bot(db_path):
    "Run the HorDoc Discord bot"
    db = sqlite_utils.Database(db_path)
    ensure_tables(db)
    run_bot(db)


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
def install(db_path):
    "Download and install models, create database"
    db = sqlite_utils.Database(db_path)
    click.echo(f"Creating tables in '{db_path}' ...")
    ensure_tables(db)
    click.echo("Installation completed.")


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument(
    "json_file",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
def import_rephrased(db_path, json_file):
    "Import rephrased JSON into the database"
    db = sqlite_utils.Database(db_path)
    ensure_tables(db)

    with open(json_file) as f:
        items = json.loads(f.read())

        db["rephrased_questions"].insert_all(
            (
                {
                    "id": item["id"],
                    "rephrased": item["rephrased"],
                    "embedding": encode(item["embeddings"]),
                }
                for item in items
            ),
            batch_size=100,
            replace=True,
        )


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument(
    "json_file",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
def import_answers(db_path, json_file):
    "Import answers JSON into the database"
    db = sqlite_utils.Database(db_path)
    ensure_tables(db)

    with open(json_file) as f:
        items = json.loads(f.read())

        db["answers"].insert_all(
            (
                {
                    "id": item["id"],
                    "question": item["question"],
                    "answer": item["answer"],
                    "messages": json.dumps([msg[0] for msg in item["messages"]]),
                }
                for item in items
            ),
            batch_size=100,
            replace=True,
        )


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument(
    "question",
    type=str,
    required=True,
)
@click.option("--top-k", "-k", type=int, default=5, show_default=True)
@click.option("--answer-certainty", "-c", type=float, default=0.75, show_default=True)
def answer_question(db_path, question, top_k, answer_certainty):
    "Try to answer a question"
    db = sqlite_utils.Database(db_path)
    ensure_tables(db)

    # idx = load_embeddings_from_json("rephrased.json")
    click.echo("Loading embeddings index...")
    idx = load_embeddings_from_db(db)
    click.echo(f"{len(idx.embeddings)} embeddings loaded")

    click.echo(f"answer_certainty={answer_certainty} top_k={top_k}")
    click.echo(f"Question: {question}")
    questions = find_most_similar_questions(idx, question, top_k=top_k)
    if questions:
        click.echo("\nThe most similar questions are:\n---")

        # lookup rephrased questions in DB
        ids = [q["id"] for q in questions]
        rephrased = find_rephrased_questions_by_ids(db, ids)

        for q in questions:
            click.echo(
                f"#{q['id']} (score {round(q['score'] * 100)}%) {rephrased[q['id']]}"
            )

        click.echo("\nThe selected answer is:\n---")
        if questions[0]["score"] > 0.75:
            # lookup answer in DB
            answer = find_answer_by_id(db, questions[0]["id"])
            click.echo(answer)
        else:
            click.echo(
                "Sorry, didn't find any close questions to derrive the answer from"
            )


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
def stats(db_path):
    "Show statistics for the given database"

    db = sqlite_utils.Database(db_path)
    rows = db.query(
        """
    select "guilds" as tbl, count(*) as cnt from guilds
    union all
    select "channels", count(*) from channels
    union all
    select "authors", count(*) from authors
    union all
    select "threads", count(*) from threads
    union all
    select "messages", count(*) from messages"""
    )
    click.echo(tabulate(list(rows), headers="keys"))
