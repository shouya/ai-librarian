import os
import atexit
import subprocess
import json
import sys
import shutil

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI

from loader import EpubBookLoader
from embedder import OpenAIEmbedder
from doc_store import ChromaDocStore
from retriever import ContextualBookRetriever

class Librarian:
    """A librarian that answers questions about a book."""

    def __init__(self, book_name, book_file):
        """Initialize the librarian."""
        self.book_name = book_name

        self.loader = EpubBookLoader(book_file)
        self.book_id = self.loader.book_id()

        self.embedder = OpenAIEmbedder()

        # make doc store persist in the xdg cache
        db_dir = os.path.expanduser(
            f"~/.cache/librarian/book/{self.book_id}"
        )
        self.doc_store = ChromaDocStore.new_local(
            f"librarian-{self.book_id}", db_dir
        )

        self.retriever = ContextualBookRetriever(
            self.loader, self.embedder, self.doc_store
        )

    def prompt(self, documents, question):
        """Generate a prompt for the librarian to answer a question."""
        if len(documents) == 0:
            raise ValueError("No documents provided.")

        sys_msg = (
            "You are a helpful assistant that answers questions "
            + f"about the book {self.book_name}. \n"
            + "You will be given the relevant portions of "
            + "the books in following messages.\n"
        )

        docs_json = [
            {
                "content": d.content,
                # "ref": str(d.id),
                # "chapter": d.metadata["chapter_title"],
            }
            for d in documents
        ]
        docs_msg = json.dumps(docs_json)
        instruct_msg = (
            "You will answer in json with all specified fields:\n\n"
            + json.dumps(
                {
                    "answer": "<your answer>",
                    "quote": "<one relevant sentence from book>",
                    # "refs": ["<ref>", "<more_ref>"],
                }
            )
            + "\n\nor if you're unable to answer the question, reply with:\n\n"
            + json.dumps({"error": "<EXPLAIN WHY YOU CANNOT ANSWER>"})
        )
        question_msg = json.dumps({"question": question})

        chat_prompt = [
            SystemMessage(content=sys_msg),
            HumanMessage(content=docs_msg),
            HumanMessage(content=instruct_msg),
            HumanMessage(content=question_msg),
        ]

        return chat_prompt

    def reload_book(self):
        """Reload the book and re-embed it."""
        self.doc_store.load()

        self.doc_store.reset()

        self.loader.parse_book()

        docs = []
        # chapter-level embeddings are not very useful from my experiments
        # docs.extend(self.loader.split_chapter_docs())
        docs.extend(self.loader.split_paragraph_docs())
        docs.extend(self.loader.split_sentence_docs())

        self.embedder.embed_docs(docs)

        self.doc_store.put(docs)
        self.doc_store.save()

    def narrow_down_documents(self, question):
        """Narrow down the documents to a few relevant ones."""
        return self.retriever.retrieve(question, 4)

    def chat(self):
        """Get a chatbot."""
        return ChatOpenAI(temperature=0.5)

    def ask_question(self, question):
        """Ask the librarian a question."""
        # Uncomment for debugging
        # return {"rel_docs": [], "answer": "DUMMY", "quote": "DUMMY"}

        documents = self.narrow_down_documents(question)
        prompt = self.prompt(documents, question)
        resp = self.chat()(prompt).content

        try:
            parsed = json.loads(resp)
        except json.JSONDecodeError:
            print(resp)
            raise "Invalid response from chatbot."

        if "error" in parsed:
            return {"error": parsed["error"]}

        return {
            "rel_docs": documents,
            "answer": parsed["answer"],
            # "refs": parsed["refs"],
            "quote": parsed["quote"],
        }


def setup_readline():
    import readline

    # use readline to get input, save history in ~/.cache/librarian/history
    readline.parse_and_bind("tab: complete")
    histfile = os.path.expanduser("~/.cache/librarian/history")
    try:
        readline.read_history_file(histfile)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass
    atexit.register(readline.write_history_file, histfile)


def interactive(librarian):
    """Ask questions interactively."""
    setup_readline()
    last_answer = {}

    while True:
        width = shutil.get_terminal_size().columns

        try:
            question = input("Question: ")
        except EOFError:
            break

        if question.strip() == "":
            continue

        if question.strip() == "!refs" or question.strip() == "!r":
            if last_answer is None:
                print("No previous answer.")
                continue

            for i, rel_doc in enumerate(last_answer["rel_docs"]):
                print(
                    # f"\nDocument {i}: {rel_doc.content.strip()[:width-20]}"
                    f"\nDocument {i}: {rel_doc.content.strip()}"
                )
            print("-" * width)
            continue

        if question.strip() == "!quit" or question.strip() == "!q":
            break

        resp = librarian.ask_question(question)

        if "error" in resp:
            print(f"Error: {resp['error']}")
            continue

        print("Answer: " + resp["answer"].strip())
        if resp["quote"] != "":
            print("\n> " + resp["quote"].strip())

        print("-" * width)
        last_answer = resp


def default_librarian():
    """Get a librarian."""
    return Librarian(
        "A Sport and a Pastime", "/home/shou/tmp/book/book.epub"
    )


def peek_docs(librarian):
    """Peek at the documents."""
    import pprint

    docs = librarian.load_documents()[0:1000]
    for doc in docs:
        pprint.pprint(doc)


def debug_query(librarian):
    setup_readline()

    while True:
        width = shutil.get_terminal_size().columns
        question = input("Question: ")

        if question.strip() == "":
            continue

        for doc in librarian.narrow_down_documents(question):
            print(f"[Document {doc.id}]")
            print(doc.content)
            print()
        print("-" * width)


def main():
    """Entry point."""
    if len(sys.argv) != 2:
        print(
            "Usage: python3 librarian.py [rebuild|chat|peek_docs|debug_query]"
        )
        return

    if sys.argv[1] == "rebuild":
        lib = default_librarian()
        lib.reload_book()
        print("Rebuilt collection.")
    elif sys.argv[1] == "chat":
        interactive(default_librarian())
    elif sys.argv[1] == "peek_docs":
        peek_docs(default_librarian())
    elif sys.argv[1] == "debug_query":
        debug_query(default_librarian())


if __name__ == "__main__":
    main()
