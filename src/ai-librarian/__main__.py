import sys

from .librarian import Librarian, interactive


def main():
    """Main entry point for the application script"""

    if len(sys.argv) == 1:
        print("Usage: ai-librarian /path/to/book.epub")
        sys.exit(1)

    epub_file = sys.argv[1]
    librarian = Librarian("Book name", epub_file)
    interactive(librarian)


if __name__ == "__main__":
    main()
