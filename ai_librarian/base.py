from abc import ABC, abstractmethod
from typing import Optional, List, NewType, Any

from pydantic import BaseModel
import numpy as np

from pydantic_numpy import NDArrayFp32

Embedding = NewType("Embedding", NDArrayFp32)
Score = NewType("Score", float)
DocId = NewType("DocId", str)


class Document(BaseModel):
    """A document that can be stored in a document store."""

    # Must be unique in a "Book"/"DocStore"
    id: DocId

    content: str
    metadata: dict

    # optional, only available if the document is retrieved
    embedding: Optional[Embedding] = None

    def to_langchain(self) -> Any:
        """Convert the document to a langchain document."""
        import langchain

        metadata = {
            "_extra": {"id": self.id, "embedding": self.embedding},
            **self.metadata,
        }

        return langchain.schema.Document(
            page_content=self.content, metadata=metadata
        )

    # should return Self
    def from_langchain(langchain_doc: Any) -> Any:
        """Convert a langchain document to a document."""
        # remove the _extra field from metadata
        extra = langchain_doc.metadata.pop("_extra")

        return Document(
            id=extra["id"],
            content=langchain_doc.page_content,
            metadata=langchain_doc.metadata,
            embedding=extra["embedding"],
        )


class DocStore(ABC):
    @abstractmethod
    def put(self, docs: List[Document]) -> None:
        """Save documents to the store."""

    @abstractmethod
    def get(self, ids: List[DocId]) -> List[Document]:
        """Load documents from the store."""

    @abstractmethod
    def dump(self) -> List[Document]:
        """Dump all documents from the store."""

    @abstractmethod
    def reset(self) -> None:
        """Delete all documents from the store."""

    @abstractmethod
    def load(self) -> None:
        """Load the document store from disk."""

    @abstractmethod
    def save(self) -> None:
        """Save the document store to disk."""

    @abstractmethod
    def exists(self) -> bool:
        """Check if the document store exists."""


class VectorDocStore(DocStore):
    @abstractmethod
    def query_by_embedding(
        self, embedding: Embedding, k: int, **kwargs: Any
    ) -> List[Document]:
        """Search for the k most similar documents."""


class Embedder(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[Embedding]:
        """Create embeddings for the texts."""

    def embed_text(self, text: str):
        """Create an embedding for a single text."""
        return self.embed_texts([text])[0]

    def embed_docs(self, docs: List[Document]):
        """Create embeddings for the documents."""
        texts = [doc.content for doc in docs]
        embeddings = self.embed_texts(texts)
        for doc, embedding in zip(docs, embeddings):
            doc.embedding = embedding


class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, k: int) -> List[Document]:
        """Retrieve the k most relevant documents to the query"""


class Loader(ABC):
    @abstractmethod
    def load(self) -> None:
        """Load a book from disk."""

    @abstractmethod
    def book_id(self) -> str:
        """Return a globally unique book id."""

    @abstractmethod
    def to_docs(self) -> List[Document]:
        """Split the book into documents."""
