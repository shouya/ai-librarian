import chromadb

from typing import List, Any
from .base import DocStore, Document, DocId, Embedding


class ChromaDocStore(DocStore):
    """A document store backed by ChromaDB."""

    client: chromadb.Client
    collection_name: str

    def new_local(collection_name: str, persist_directory: str):
        """Create a new ChromaDocStore backed by a local directory."""
        settings = chromadb.config.Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory,
            anonymized_telemetry=False,
        )
        client = chromadb.Client(settings)
        return ChromaDocStore(client, collection_name)

    def __init__(self, client, collection_name):
        """Create a new ChromaDocStore."""
        self.client = client
        self.collection_name = collection_name

    def collection(self):
        """Get the ChromaDB collection."""
        if hasattr(self, "_collection"):
            return self._collection

        self._collection = self.get_or_create_collection(
            self.collection_name
        )
        return self._collection

    def query_by_embedding(
        self, embedding: Embedding, k: int, **kwargs: Any
    ) -> List[Document]:
        """Query the document store by embedding."""
        coll = self.collection()
        results = coll.query(
            query_embeddings=embedding,
            n_results=4,
            include=["metadatas", "documents", "distances", "embeddings"],
            **kwargs
        )
        return _results_to_docs(results)

    def put(self, docs: List[Document]) -> None:
        """Save documents to the store."""
        documents = []
        metadatas = []
        ids = []
        embeddings = []

        for doc in docs:
            documents.append(doc.page_content)
            metadatas.append(doc.metadata)
            ids.append(doc.id)
            embeddings.append(doc.embedding)

        self.collection().add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings,
        )

    def get(self, ids: List[DocId]) -> List[Document]:
        """Load documents from the store."""
        coll = self.collection()
        results = coll.get(
            ids=ids, include=["metadatas", "documents", "embeddings"]
        )
        return _results_to_docs(results)

    def reset(self) -> None:
        """Reset the document store."""
        self.client.delete_collection(self.collection_name)

    def load(self) -> None:
        """Load the document store from disk."""
        pass

    def save(self) -> None:
        """Save the document store to disk."""
        self.client.persist()


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
