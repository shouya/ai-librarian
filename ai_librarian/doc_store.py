import chromadb
import numpy as np
import os

from typing import List, Any

from .base import VectorDocStore, Document, DocId, Embedding


class ChromaDocStore(VectorDocStore):
    """A document store backed by ChromaDB."""

    client: chromadb.Client
    collection_name: str

    @staticmethod
    def new_local(collection_name: str, persist_directory: str):
        """Create a new ChromaDocStore backed by a local directory."""
        settings = chromadb.config.Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory,
            anonymized_telemetry=False,
        )
        client = chromadb.Client(settings)
        return ChromaDocStore(client, collection_name)

    @staticmethod
    def new_local_readonly(
        collection_name: str, persistent_directory: str
    ):
        """Create a readonly ChromaDocStore backed by a local directory."""
        store = ChromaDocStore.new_local(
            collection_name, persistent_directory
        )
        store.readonly = True
        return store

    def __init__(self, client, collection_name):
        """Create a new ChromaDocStore."""
        self.client = client
        self.collection_name = collection_name
        self.readonly = False

    def collection(self):
        """Get the ChromaDB collection."""
        if self.readonly:
            return self.client.get_collection(
                self.collection_name, embedding_function=dummy_embedding
            )

        return self.client.get_or_create_collection(
            self.collection_name,
            embedding_function=dummy_embedding,
        )

    def query_by_embedding(
        self, embedding: Embedding, k: int, **kwargs: Any
    ) -> List[Document]:
        """Query the document store by embedding."""
        coll = self.collection()
        results = coll.query(
            query_embeddings=[list(embedding)],
            n_results=k,
            include=["metadatas", "documents", "embeddings"],
            **kwargs,
        )
        results["ids"] = results["ids"][0]
        results["metadatas"] = results["metadatas"][0]
        results["documents"] = results["documents"][0]
        results["embeddings"] = results["embeddings"][0]
        return _results_to_docs(results)

    def put(self, docs: List[Document]) -> None:
        """Save documents to the store."""
        if self.readonly:
            raise Exception("Cannot put documents in a readonly store.")

        if len(docs) == 0:
            return

        documents = []
        metadatas = []
        ids = []
        embeddings = []

        for doc in docs:
            documents.append(doc.content)
            metadatas.append(
                {k: v for k, v in doc.metadata.items() if v is not None}
            )
            ids.append(doc.id)
            embeddings.append(doc.embedding)

        print(documents)
        print(metadatas)
        print(ids)
        print(embeddings)

        coll = self.collection()
        coll.add(
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

    def dump(self) -> List[Document]:
        """Dump all documents from the store."""
        coll = self.collection()
        results = coll.get(
            include=["metadatas", "documents", "embeddings"]
        )
        return _results_to_docs(results)

    def reset(self) -> None:
        """Reset the document store."""
        if self.readonly:
            raise Exception("Cannot reset a readonly store.")
        self.client.delete_collection(self.collection_name)

    def load(self) -> None:
        """Load the document store from disk."""
        # calling this function initializes the collection
        _ = self.collection()
        pass

    def save(self) -> None:
        """Save the document store to disk."""
        if self.readonly:
            raise Exception("A readonly store cannot be saved.")

        self.client.persist()

    def exists(self) -> bool:
        """Check if the document store exists."""
        result = self.collection().peek(n_results=1, include=[])
        return result["ids"] != []


def _results_to_docs(results: Any) -> List[Document]:
    docs = []

    count = len(results["ids"])
    for i in range(count):
        metadata = results["metadatas"][i]
        if metadata is None:
            metadata = {}

        embedding = results["embeddings"][i]
        content = results["documents"][i]
        id_ = results["ids"][i]

        doc = Document(
            id=id_,
            content=content,
            metadata=metadata,
            embedding=np.asarray(embedding),
        )
        docs.append(doc)

    return docs


def dummy_embedding(_any):
    raise NotImplementedError("should be unreachable!")


class BookStoreFactory:
    @staticmethod
    def readonly(book_id, book_dir) -> VectorDocStore:
        """Get the document store."""
        collection_name = f"librarian-{book_id}"
        store_dir = os.path.join(book_dir, "store")
        return ChromaDocStore.new_local_readonly(
            collection_name, store_dir
        )

    @staticmethod
    def mutable(book_id, book_dir) -> VectorDocStore:
        """Get the document store."""
        collection_name = f"librarian-{book_id}"
        store_dir = os.path.join(book_dir, "store")
        return ChromaDocStore.new_local(collection_name, store_dir)
