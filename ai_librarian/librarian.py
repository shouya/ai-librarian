import os
import atexit
import subprocess
import json
import sys
import shutil
import uuid

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI

from .loader import EpubBookLoader
from .embedder import OpenAIEmbedder
from .doc_store import ChromaDocStore
from .retriever import ContextualBookRetriever
from .library import Library


class Librarian:
    """A librarian that answers questions about a book."""

    @staticmethod
    def from_file(book_file):
        """Create a librarian from a book file."""
        loader = EpubBookLoader(book_file)
        book_id = loader.book_id()

        book_dir = os.path.expanduser(f"~/.cache/librarian/book/{book_id}")
        if not os.path.exists(book_dir):
            os.makedirs(book_dir)
            shutil.copy(book_file, book_dir)

        return Librarian(book_id, loader)

    def __init__(self, book_id, loader=None):
        """Initialize the librarian."""
        self.book_id = book_id
        self.loader = loader

        self.embedder = OpenAIEmbedder()

        # make doc store persist in the xdg cache
        self.book_dir = os.path.expanduser(
            f"~/.cache/librarian/book/{self.book_id}"
        )

        store_dir = os.path.join(self.book_dir, "store")
        if not os.path.exists(store_dir):
            # calling ChromaDocStore.new_local will create the
            # store_dir, thus we must check if it exists first
            self.doc_store = ChromaDocStore.new_local(
                f"librarian-{self.book_id}", store_dir
            )
            self.reload_book()
        else:
            self.doc_store = ChromaDocStore.new_local(
                f"librarian-{self.book_id}", store_dir
            )

        self.retriever = ContextualBookRetriever(
            self.embedder, self.doc_store
        )

    def prompt(self, documents, question):
        """Generate a prompt for the librarian to answer a question."""
        if len(documents) == 0:
            raise ValueError("No documents provided.")

        sys_msg = (
            "You are a helpful assistant that answers questions about a book.\n"
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
        if self.loader is None:
            raise ValueError("Book is read-only.")

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

    def narrow_down_documents(self, question):
        """Narrow down the documents to a few relevant ones."""
        return self.retriever.retrieve(question, 4)

    def chat(self):
        """Get a chatbot."""
        return ChatOpenAI(temperature=0.5)

    def ask_question_logged(self, question):
        """Ask the librarian a question and log it."""
        resp = self.ask_question_raw(question)

        answer = resp.get("answer")
        log_id = str(uuid.uuid4())
        rel_docs = [
            {k: v for k, v in doc.dict().items() if k != "embedding"}
            for doc in resp.get("rel_docs", [])
        ]

        extra = {
            "error": resp.get("error"),
            "quote": resp.get("quote"),
            "rel_docs": rel_docs,
        }

        library = Library.instance()
        library.add_chat_log(self.book_id, log_id, question, answer, extra)

        return {
            "question": question,
            "answer": answer,
            "log_id": log_id,
            **extra,
        }

    def ask_question_raw(self, question):
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

        resp = librarian.ask_question_logged(question)

        if resp.get("error"):
            print(f"Error: {resp['error']}")
            continue

        print("Answer: " + resp["answer"].strip())
        if resp["quote"] != "":
            print("\n> " + resp["quote"].strip())

        print("-" * width)
        last_answer = resp


def interactive_debug_query(librarian):
    setup_readline()

    while True:
        width = shutil.get_terminal_size().columns
        question = input("Question: ")

        if question.strip() == "":
            continue

        for doc in librarian.narrow_down_documents(question):
            chapter = doc.metadata["chapter_title"]
            heading = f"[Document {doc.id} from chapter {chapter}]"
            print(heading, end="")
            print((width - len(heading)) * "-")
            print(doc.content)
            print()
        print("=" * width)
