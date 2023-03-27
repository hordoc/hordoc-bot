#!/usr/bin/env python3

import os

from dotenv import load_dotenv
import click
import sqlite_utils
from tabulate import tabulate

from hordoc.bot import client
from hordoc.data import ensure_tables

load_dotenv()


@click.group()
@click.version_option()
def cli():
    "HorDoc: AI-Powered Discord Community Support"


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
