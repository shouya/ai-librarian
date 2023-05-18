import os
import shutil

from .doc_store import ChromaDocStore
from .base import Document, Embedding, VectorDocStore
from .loader import EpubBookLoader
from .util import get_book_dir, get_embedder


class Indexer:
    @staticmethod
    def unindex(book_dir):
        """Unindex a book."""
        shutil.rmtree(book_dir)

    def __init__(self, book_file):
        """Create a new indexer."""
        self.book_file = book_file

        self.loader = EpubBookLoader(book_file)
        self.book_id = self.loader.book_id()

        self.book_dir = get_book_dir(self.book_id)

        self.embedder = get_embedder()

        store_dir = os.path.join(self.book_dir, "store")
        self.doc_store = ChromaDocStore.new_local(
            f"librarian-{self.book_id}", store_dir
        )

    def index(self, force=False):
        """Index the book.

        If force is True, the book will be re-indexed even if it has
        already been indexed."""

        if not force and self.doc_store.exists():
            return

        self.copy_book_file()
        print("Book file copied.")

        self.doc_store.load()
        self.doc_store.reset()
        print("Book index reset.")

        self.loader.load()
        print("Book loaded.")

        docs = self.loader.to_docs()
        print("Book fragments generated.")

        self.embedder.embed_docs(docs)
        print("Embedding generated.")

        self.doc_store.put(docs)
        self.doc_store.save()
        print("Book index saved.")

    def copy_book_file(self):
        """Copy the book file to the book directory."""
        if not os.path.exists(self.book_dir):
            os.makedirs(self.book_dir)

        ext_name = os.path.splitext(self.book_file)[1]
        new_name = f"book{ext_name}"
        new_path_name = os.path.join(self.book_dir, new_name)
        shutil.copy(self.book_file, new_path_name)

    def indexed(self) -> bool:
        """Check if the book is indexed."""
        return self.doc_store.exists()
