"""The entry point for the LangChain library."""

import os
import subprocess
import json
import sys

from pprint import pprint

from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.vectorstores import Chroma
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI

SCRIPT_DIR = sys.path[0]

output = subprocess.check_output("pass show openai/api-key", shell=True)
os.environ["OPENAI_API_KEY"] = output.decode().strip()


class Librarian:
    """A librarian that answers questions about a book."""

    def __init__(self, book_name, book_file):
        """Initialize the librarian."""
        self.book_name = book_name
        self.book_file = book_file

        self.embedding = OpenAIEmbeddings()

        self.text_splitter = CharacterTextSplitter(
            chunk_size=2000, chunk_overlap=10
        )
        self.chroma_dir = "/home/shou/tmp/chroma"
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

    def load_documents(self):
        """Load the documents from the book file."""
        loader = TextLoader(self.book_file)
        splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=10)
        documents = splitter.split_documents(loader.load())
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

    def narrow_down_documents(self, vectordb, question, k=3):
        """Narrow down the documents to the most relevant."""
        retriever = vectordb.as_retriever(
            search_type="mmr", search_kwargs={"k": k}
        )
        return retriever.get_relevant_documents(question)

    def chat(self):
        """Get a chatbot."""
        return ChatOpenAI(temperature=0)

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
            "answer": parsed["answer"],
            # "refs": parsed["refs"],
            "quote": parsed["quote"],
        }


def interactive(librarian):
    """Ask questions interactively."""
    while True:
        question = input("Question: ")
        resp = librarian.ask_question(question)
        if "error" in resp:
            print(resp["error"])
        else:
            print(">>> " + resp["answer"])
            print("")
            print("Quote: " + resp["quote"] + "\n")


def librarian():
    """Get a librarian."""
    return Librarian(
        "A Sport and a Pastime", "/home/shou/tmp/book/book.txt"
    )


def main():
    """Entry point."""
    l = librarian()
    interactive(l)


if __name__ == "__main__":
    main()
