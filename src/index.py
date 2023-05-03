import os
import atexit
import subprocess
import json
import sys
import shutil

from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, UnstructuredEPubLoader
from langchain.vectorstores import Chroma
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI


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

        os.environ["OPENAI_API_KEY"] = openai_key()
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
            {"content": d.page_content, "ref": d.metadata["cite_id"]}
            for d in documents
        ]
        docs_msg = json.dumps(docs_json)
        question_msg = json.dumps({"question": question})
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

        chat_prompt = [
            SystemMessage(content=sys_msg),
            HumanMessage(content=docs_msg),
            HumanMessage(content=instruct_msg),
            HumanMessage(content=question_msg),
        ]

        return chat_prompt

    def load_raw_documents(self):
        """Load the raw documents from the book file."""
        if self.book_file.endswith(".txt"):
            loader = TextLoader(self.book_file)
        elif self.book_file.endswith(".epub"):
            loader = UnstructuredEPubLoader(
                self.book_file, mode="elements"
            )
        else:
            raise ValueError(
                f"Unsupported file type: {self.book_file}. "
                + "Only .txt and .epub are supported."
            )

        return loader.load()

    def load_documents(self):
        """Load the documents from the book file and split to chunks."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=200, chunk_overlap=0
        )
        documents = splitter.split_documents(self.load_raw_documents())
        for id, doc in enumerate(documents):
            doc.metadata["cite_id"] = id
            doc.metadata["book"] = self.book_name
        return documents

    def vectordb(self, force_rebuild=False):
        """Get the vector database."""
        if self._vectordb is not None and not force_rebuild:
            return self._vectordb

        if os.path.exists(self.chroma_dir) and not force_rebuild:
            self._vectordb = Chroma(
                persist_directory=self.chroma_dir,
                embedding_function=self.embedding,
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

    def narrow_down_documents(self, vectordb, question, k=10):
        """Narrow down the documents to the most relevant."""
        retriever = vectordb.as_retriever(
            search_type="mmr", search_kwargs={"k": k}
        )
        return retriever.get_relevant_documents(question)

    def chat(self):
        """Get a chatbot."""
        return ChatOpenAI(temperature=0.5)

    def ask_question(self, question):
        """Ask the librarian a question."""
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


def interactive(librarian):
    """Ask questions interactively."""
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

    last_answer = None

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
        "A Sport and a Pastime", "/home/shou/tmp/book/book.txt"
    )


def peek_docs(librarian):
    """Peek at the documents."""
    import pprint

    docs = librarian.load_raw_documents()[0:1000]
    for doc in docs:
        pprint.pprint(doc)


def main():
    """Entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 librarian.py [rebuild|chat|peek_docs]")
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


if __name__ == "__main__":
    main()
