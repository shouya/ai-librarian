import click

import sys

from .librarian import Librarian, interactive, debug_query


@click.group()
def cli():
    pass


@cli.command(help="Start asking questions about the book")
@click.option("-f", "--file", required=True, help="Path to the epub file")
def chat(file):
    librarian = Librarian(file)
    interactive(librarian)


@cli.command(help="Debug a query")
@click.option("-f", "--file", required=True, help="Path to the epub file")
def debug_query(file):
    librarian = Librarian(file)
    debug_query(librarian)


@cli.command(help="Rebuild the index")
@click.option("-f", "--file", required=True, help="Path to the epub file")
def rebuild(file):
    librarian = Librarian(file)
    librarian.reload_book()
    print("Rebuilt index.")
