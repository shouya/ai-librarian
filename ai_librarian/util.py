import os

from .const import LIBRARIAN_DIR
from .base import Embedder
from .embedder import OpenAIEmbedder


def get_book_dir(book_id: str) -> str:
    """Get the directory for the book."""
    return os.path.join(LIBRARIAN_DIR, book_id)


def get_embedder() -> Embedder:
    """Get the embedder."""
    return OpenAIEmbedder()
