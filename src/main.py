import os
import atexit
import subprocess
import json
import sys
import shutil

from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI

from loader import EpubBookLoader


def openai_key():
    """Get the OpenAI API key."""
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ.get("OPENAI_API_KEY")
    # try retrieve from a cached global variable to avoid calling subprocess
    # if not found, call subprocess and cache it

    if not hasattr(openai_key, "key"):
        openai_key.key = (
            subprocess.check_output("pass show openai/api-key", shell=True)
            .decode("utf-8")
            .strip()
        )
    return openai_key.key


class Librarian:
    """A librarian that answers questions about a book."""

    def __init__(self, book_name, book_file):
        """Initialize the librarian."""
        self.book_name = book_name
        self.book_file = book_file

        openai.api_key = openai_key()
        self.embedding = OpenAIEmbeddings()

        # store it in the xdg cache
        self.chroma_dir = os.path.expanduser("~/.cache/librarian/chroma")
        self._vectordb = None

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
            {"content": d.page_content, "ref": str(d.metadata["cite_id"])}
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

    def load_documents(self):
        """Load the documents from the book file and split to chunks."""
        loader = EpubBookLoader(self.book_file)
        loader.parse_book()

        docs = []

        # chapter-level embeddings are not very useful from my experiments
        # docs.extend(loader.split_chapter_docs())

        docs.extend(loader.split_paragraph_docs())
        docs.extend(loader.split_sentence_docs())

        loader.store_docs(docs)

        return docs

    def vectordb(self, force_rebuild=False):
        """Get the vector database."""
        if self._vectordb is not None and not force_rebuild:
            return self._vectordb

        if os.path.exists(self.chroma_dir) and not force_rebuild:
            self._vectordb = Chroma(
                persist_directory=self.chroma_dir,
                embedding_function=self.embedding,
                settings={"anonymized_telemetry": False},
            )
        else:
            os.makedirs(self.chroma_dir, exist_ok=True)
            shutil.copyfile(
                self.book_file, os.path.join(self.chroma_dir, "book.txt")
            )

            documents = self.load_documents()
            vectordb = Chroma.from_documents(
                persist_directory=self.chroma_dir,
                embedding=self.embedding,
                documents=documents,
            )
            vectordb.persist()
            self._vectordb = vectordb

        return self._vectordb

    def clear_collection(self):
        """Clear the collection."""
        if os.path.exists(self.chroma_dir):
            import shutil

            shutil.rmtree(self.chroma_dir)

    def narrow_down_documents(self, q, k=10):
        """Narrow down the documents to the most relevant."""
        vectordb = self.vectordb()
        retriever = vectordb.as_retriever(
            search_type="mmr", search_kwargs={"k": k}
        )
        return retriever.get_relevant_documents(q)

    def narrow_down_documents(self, q, k=10):
        """Narrow down the documents to the most relevant."""
        vectordb = self.vectordb()
        docs = []
        for d, score in vectordb.max_marginal_relevance_search(
            q, k, fetch_k=k * 5
        ):
            d.metadata["score"] = score
            docs.append(d)
        return docs

    def chat(self):
        """Get a chatbot."""
        return ChatOpenAI(temperature=0.5)

    def ask_question(self, question):
        """Ask the librarian a question."""
        return {"rel_docs": [], "answer": "DUMMY", "quote": "DUMMY"}

        vectordb = self.vectordb()
        documents = self.narrow_down_documents(vectordb, question)
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
                    # f"\nDocument {i}: {rel_doc.page_content.strip()[:width-20]}"
                    f"\nDocument {i}: {rel_doc.page_content.strip()}"
                )
            print("-" * width)
            continue

        if question.strip() == "!quit" or question.strip() == "!q":
            break

        resp = librarian.ask_question(question)

        if "error" in resp:
            print(resp["error"])
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

    vectordb = librarian.vectordb()
    while True:
        width = shutil.get_terminal_size().columns
        question = input("Question: ")

        if question.strip() == "":
            continue

        for doc in librarian.narrow_down_documents(vectordb, question):
            cite_id = doc.metadata["cite_id"]
            score = doc.metadata["score"]
            print(f"[Document {cite_id}: {score:.4f}]")
            print(doc.page_content)
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
        lib.clear_collection()
        lib.vectordb(force_rebuild=True)
        print("Rebuilt collection.")
    elif sys.argv[1] == "chat":
        interactive(default_librarian())
    elif sys.argv[1] == "peek_docs":
        peek_docs(default_librarian())
    elif sys.argv[1] == "debug_query":
        debug_query(default_librarian())


if __name__ == "__main__":
    main()
