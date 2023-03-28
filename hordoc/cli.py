#!/usr/bin/env python3

import json
import os

from dotenv import load_dotenv
import click
import sqlite_utils
from tabulate import tabulate

from hordoc.bot import client
from hordoc.data import ensure_tables
from hordoc.embeddings.embeddings_search import encode

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
    client.run(os.environ["DISCORD_SECRET"])


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
def import_embeddings(db_path, json_file):
    "Import embeddings JSON into the database"
    db = sqlite_utils.Database(db_path)
    ensure_tables(db)

    with open(json_file) as f:
        items = json.loads(f.read())

        db["message_embeddings"].insert_all(
            (
                {
                    "id": item["id"],
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
                    "messages": json.dumps(item["messages"]),
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
