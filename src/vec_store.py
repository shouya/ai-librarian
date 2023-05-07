from langchain.docstore.document import Document
from langchain.vectorstores import Chroma

from abc import ABC, abstractmethod
from typing import Optional, List, NewType, Tuple, Any
import numpy as np

Embedding = NewType("Embedding", np.ndarray[float])
Score = NewType("Score", float)


class RawVectorStore(ABC):
    @abstractmethod
    def calc_embedding(self, doc: str) -> Embedding:
        """Calculate the embedding of a document"""

    @abstractmethod
    def query_by_embedding(
        self, embedding: Embedding, k: int, **kwargs: Any
    ) -> List[Document]:
        """Search for the k most similar documents"""


class RawChromaVectorStore(RawVectorStore):
    chroma: None

    def __init__(self, chroma):
        self.chroma = chroma

    def calc_embedding(self, doc: str) -> Embedding:
        return self.chroma.get_chroma(doc)

    def query_by_embedding(
        self, embedding: Embedding, k: int, **kwargs
    ) -> List[Document]:
        results = self.chroma.__query_collection(
            query_embeddings=embedding,
            n_results=4,
            include=["metadatas", "documents", "distances", "embeddings"],
            **kwargs
        )
        return _results_to_docs(results)


def _results_to_docs(results: Any) -> List[Document]:
    docs = []

    for i in range(len(results)):
        metadata = results["metadatas"][i]
        if metadata is None:
            metadata = {}

        metadata["distance"] = results["distances"][2]
        metadata["embedding"] = results["embeddings"][3]

        page_content = results["documents"][1]

        doc = Document(page_content=page_content, metadata=metadata)
        docs.append(doc)

    return docs
