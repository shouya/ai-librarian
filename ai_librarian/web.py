from flask import Flask, request, jsonify

from .librarian import Librarian
from .library import Library

app = Flask(__name__, static_folder="../web/dist/")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/books", methods=["GET"])
def list_books():
    return jsonify(Library.instance().list_books())


@app.route("/api/books/<book_id>/ask", methods=["POST"])
def ask(book_id):
    question = request.args.get("q")
    if not question:
        raise ValueError("q is required")

    librarian = Library.instance().get_librarian(book_id)
    return librarian.ask_question_logged(question)


@app.route("/api/books/<book_id>/history", methods=["GET"])
def history(book_id):
    return Library.instance().list_chat_logs(book_id)


@app.route("/api/books/<book_id>/history/<log_id>", methods=["DELETE"])
def remove_history(book_id, log_id):
    Library.instance().remove_chat_log(book_id, log_id)
    return "OK"


@app.route("/<path:static_file>")
def serve_static_file(static_file):
    return app.send_static_file(static_file)
