import click

import sys

from .librarian import Librarian, interactive, interactive_debug_query


@click.group()
def cli():
    pass


@cli.command(help="Start asking questions about the book")
@click.option("-f", "--file", required=True, help="Path to the epub file")
def chat(file):
    librarian = Librarian.from_file(file)
    interactive(librarian)


@cli.command(help="Debug a query")
@click.option("-f", "--file", required=True, help="Path to the epub file")
def debug_query(file):
    librarian = Librarian.from_file(file)
    interactive_debug_query(librarian)


@cli.command(help="Rebuild the index")
@click.option("-f", "--file", required=True, help="Path to the epub file")
def rebuild(file):
    librarian = Librarian.from_file(file)
    librarian.reload_book()
    print("Rebuilt index.")


@cli.command(help="Start web interface")
@click.option("-h", "--host", default="127.0.0.1")
@click.option("-p", "--port", default=5000)
def web(host, port):
    from .web import app

    app.run(host=host, port=port)
