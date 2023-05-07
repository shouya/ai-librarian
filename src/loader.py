import ebooklib
import epub_meta
from ebooklib import epub
from bs4 import BeautifulSoup as BS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

import pprint

"""
The structure of a parsed book:
{
    "title": "<TITLE>",
    "chapters": [
        {
          "index": <NO>,
          "title": "<TITLE>",
          "paragraphs": [
            "<PARAGRAPH>",
          ]
        },
        ...
    ]
}
"""


class BookLoader:
    """Load and parse the structure of a source book file"""

    def __init__(self, file_path):
        """Initialize a book loader"""
        self.file_path = file_path
        self.structure = None

    def parse_book(self):
        """Parse the book file"""
        raise NotImplementedError


class EpubBookLoader(BookLoader):
    epub = None
    chapters = None
    cite_index = {}

    def parse_book(self):
        """Parse the book file"""
        self.epub = epub.read_epub(self.file_path)
        self.chapters = self._parse_chapters(self.epub)

    def _parse_chapters(self, epub):
        """Parse the chapters of the book"""
        chapters = []
        for item in epub.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            dom = BS(item.get_content(), "xml")
            title = dom.find("h1") or dom.find("h2") or dom.find("h3")
            if not title:
                continue
            title = title.text

            paragraphs = [p.text for p in dom.find_all("p")]
            if len(paragraphs) == 0 or len(paragraphs[0]) == 0:
                continue

            chapter = {"title": title, "paragraphs": paragraphs}
            chapters.append(chapter)

        for i in range(len(chapters)):
            chapters[i]["index"] = i
        return chapters

    def to_langchain_docs(self):
        """Convert the book to a list of langchain documents"""
        docs = []
        for chapter in self.chapters:
            doc = Document(
                page_content="\n\n".join(chapter["paragraphs"]),
                metadata={
                    "chapter_index": chapter["index"],
                    "chapter_title": chapter["title"],
                },
            )
            docs.append(doc)
        return docs

    def _split_docs(self, level, splitter_conf):
        splitter = RecursiveCharacterTextSplitter(**splitter_conf)
        docs = []
        for doc in self.to_langchain_docs():
            split_docs = splitter.create_documents([doc.page_content])
            for part_no, split_doc in enumerate(split_docs):
                split_doc.metadata = doc.metadata.copy()

                chapter_index = doc.metadata["chapter_index"]
                part = f"{part_no+1}/{len(split_docs)}"
                cite_id = f"{level}:{chapter_index}:{part}"
                split_doc.metadata["cite_id"] = cite_id

                split_doc.metadata["prev_id"] = None
                split_doc.metadata["next_id"] = None

                docs.append(split_doc)

        for i in range(1, len(docs)):
            docs[i].metadata["prev_id"] = docs[i - 1].metadata["cite_id"]

        for i in range(0, len(docs) - 1):
            docs[i].metadata["next_id"] = docs[i + 1].metadata["cite_id"]

        return docs

    def split_chapter_docs(self):
        return self._split_docs(
            "chapter", {"chunk_size": 2000, "chunk_overlap": 100}
        )

    def split_paragraph_docs(self):
        return self._split_docs(
            "paragraph", {"chunk_size": 800, "chunk_overlap": 0}
        )

    def split_sentence_docs(self):
        return self._split_docs(
            "sentence", {"chunk_size": 200, "chunk_overlap": 0}
        )

    def store_docs(self, docs):
        for doc in docs:
            doc_id = doc.metadata["cite_id"]
            self.cite_index[doc_id] = doc


if __name__ == "__main__":
    loader = EpubBookLoader("/home/shou/tmp/book/book.epub")
    loader.parse_book()
    pprint.pprint(loader.split_chapter_docs()[10])
