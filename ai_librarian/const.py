import os

DEFAULT_LIBRARIAN_DIR = "~/.cache/librarian"

LIBRARIAN_DIR = os.path.expanduser(
    os.environ.get("DATA_DIR", DEFAULT_LIBRARIAN_DIR)
)
