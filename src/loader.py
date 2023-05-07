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

    def split_chapter_docs(self):
        """Split the book into chapter-sized documents"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=100,
        )
        docs = []
        for doc in self.to_langchain_docs():
            split_docs = splitter.create_documents([doc.page_content])
            for part_no, split_doc in enumerate(split_docs):
                split_doc.metadata = doc.metadata
                part = f"{part_no+1}/{len(split_docs)}"
                split_doc.metadata["part_of_chapter"] = part
                split_doc.metadata["level"] = "chapter"
                docs.append(split_doc)

        return docs

    def split_sentence_docs(self):
        """Split the book into sentence-sized documents"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=0,
        )
        docs = []
        for doc in self.to_langchain_docs():
            split_docs = splitter.create_documents([doc.page_content])
            for part_no, split_doc in enumerate(split_docs):
                split_doc.metadata = doc.metadata.copy()
                part = f"{part_no+1}/{len(split_docs)}"
                split_doc.metadata["part_of_chapter"] = part
                split_doc.metadata["level"] = "sentence"
                docs.append(split_doc)

        return docs


if __name__ == "__main__":
    loader = EpubBookLoader("/home/shou/tmp/book/book.epub")
    loader.parse_book()
    pprint.pprint(loader.split_chapter_docs()[10])
