from typing import List, Tuple
import sqlite3
import json
import os

from .const import LIBRARIAN_DIR


class BookKeeper:
    """BookKeeper is a class that manages the database of books and chat logs."""

    _instance = None

    @staticmethod
    def instance():
        """Get the singleton instance of the book keeper."""
        if BookKeeper._instance is None:
            BookKeeper._instance = BookKeeper()
        return BookKeeper._instance

    def __init__(self, conf_dir=LIBRARIAN_DIR):
        """Initialize the book keeper with the path to the configuration directory."""
        db_path = os.path.expanduser(conf_dir + "/book keeper.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_schema()

    def create_schema(self):
        """Create the database schema if it does not exist."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                book_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_logs (
                log_id TEXT PRIMARY KEY,
                book_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT,
                extra TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books (book_id)
            );
            """
        )
        self.conn.commit()

    def add_book(self, name, book_file, force=False):
        """Index a new book and add to library."""
        indexer = Indexer(book_file)
        book_id = indexer.book_id

        if self.book_exists(book_id) and not force:
            raise ValueError("Book already exists.")

        indexer.index(force=True)

        self.register_book(name, book_id)
        return book_id    

    def deregister_book(self, book_id):
        """Remove a book from the book keeper."""
        self.conn.execute(
            """
            DELETE FROM books
            WHERE book_id = ?
            """,
            (book_id,),
        )
        self.conn.commit()

    def delete_book(self, book_id):
        """Remove a book from the book keeper and delete its index."""
        self.deregister_book(book_id)
        Indexer.unindex(book_id)

    def register_book(self, name, book_id):
        """Add a book to the book keeper."""
        self.conn.execute(
            """
            INSERT INTO books (name, book_id)
            VALUES (?, ?)
            """,
            (name, book_id),
        )
        self.conn.commit()

    def add_chat_log(self, book_id, log_id, question, answer, extra):
        """Add a chat log to the book keeper."""
        extra = json.dumps(extra)
        self.conn.execute(
            """
            INSERT INTO chat_logs (book_id, log_id, question, answer, extra)
            VALUES (?, ?, ?, ?, ?)
            """,
            (book_id, log_id, question, answer, extra),
        )
        self.conn.commit()

    def remove_chat_log(self, book_id, log_id):
        """Remove a chat log from the book keeper."""
        self.conn.execute(
            """
            DELETE FROM chat_logs
            WHERE book_id = ? AND log_id = ?
            """,
            (book_id, log_id),
        )
        self.conn.commit()

    def list_books(self) -> List[dict]:
        """List all books in the book keeper."""
        cursor = self.conn.execute(
            """
            SELECT book_id, name
            FROM books
            """
        )
        return [
            {"book_id": book_id, "name": name}
            for book_id, name in cursor.fetchall()
        ]

    def list_chat_logs(self, book_id):
        """List all chat logs for a book."""
        cursor = self.conn.execute(
            """
            SELECT log_id, question, answer, extra
            FROM chat_logs
            WHERE book_id = ?
            """,
            (book_id,),
        )

        return [
            {
                "book_id": book_id,
                "log_id": log_id,
                "question": question,
                "answer": answer,
                **json.loads(extra),
            }
            for log_id, question, answer, extra in cursor.fetchall()
        ]

    def register_book(self, book_name, path_to_book):
        """Register a new book to the book keeper."""
        from .librarian import Librarian

        librarian = Librarian.from_file(path_to_book)
        librarian.reload_book()
        self.add_book(book_name, librarian.book_id)

    def book_exists(self, book_id):
        """Check if a book exists."""
        cursor = self.conn.execute(
            """
            SELECT book_id
            FROM books
            WHERE book_id = ?
            """,
            (book_id,),
        )
        return cursor.fetchone() is not None

    def get_librarian(self, book_id):
        """Get a librarian for a book."""
        from .librarian import Librarian

        if self.book_exists(book_id):
            return Librarian(book_id)


if __name__ == "__main__":
    lib = BookKeeper()
    lib.add_book(
        "A Sport and a Pastime", "5aaab36d14b7f88f326d537e395ffab9"
    )
    print(lib.list_chat_logs("5aaab36d14b7f88f326d537e395ffab9"))
    print(LIBRARIAN_DIR)
