import os

from .const import LIBRARIAN_DIR
from .base import Embedder
from .embedder import OpenAIEmbedder


def get_book_dir(book_id: str) -> str:
    """Get the directory for the book."""
    book_dir = os.path.join(LIBRARIAN_DIR, "book")
    return os.path.join(book_dir, book_id)


def get_embedder() -> Embedder:
    """Get the embedder."""
    return OpenAIEmbedder()
