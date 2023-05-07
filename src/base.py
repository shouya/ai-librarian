from abc import ABC, abstractmethod
from typing import Optional, List, NewType, Tuple, Any
from pydantic import BaseModel
import numpy as np

Embedding = NewType("Embedding", np.ndarray[float])
Score = NewType("Score", float)
DocId = NewType("DocId", str)


class Document(BaseModel):
    """A document that can be stored in a document store"""

    id: DocId
    content: str
    metadata: dict

    # optional, only available if the document is retrieved
    embedding: Optional[Embedding] = None


class DocStore(ABC):
    @abstractmethod
    def query_by_embedding(
        self, embedding: Embedding, k: int, **kwargs: Any
    ) -> List[Document]:
        """Search for the k most similar documents"""

    @abstractmethod
    def put(self, docs: List[Document]) -> None:
        """Save documents to the store."""

    @abstractmethod
    def get(self, ids: List[DocId]) -> List[Document]:
        """Load documents from the store."""

    @abstractmethod
    def reset(self) -> None:
        """Delete all documents from the store."""

    @abstractmethod
    def load(self) -> None:
        """Load the document store from disk."""

    @abstractmethod
    def save(self) -> None:
        """Save the document store to disk."""


class Retriever(ABC):
    @abstractmethod
    def retrieve(
        self, query: str, k: int, **kwargs: Any
    ) -> List[Document]:
        """Retrieve the k most relevant documents to the query"""


class Embedder(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[Embedding]:
        """Create embeddings for the texts"""

    @abstractmethod
    def embed_text(self, text: str):
        """Create an embedding for a single text"""
        return self.embed_texts([text])[0]

    @abstractmethod
    def embed_docs(self, docs: List[Document]):
        """Create embeddings for the documents"""
        texts = [doc.content for doc in docs]
        embeddings = self.embed_texts(texts)
        for doc, embedding in zip(docs, embeddings):
            doc.embedding = embedding
